#!python3
from urllib import request
import requests
import argparse
import json
from datetime import datetime
import urllib.parse
import csv

lang_long = ["arabic", "bulgarian", "schinese", "tchinese", "czech", "danish", "dutch", "english", "finnish", "french", "german", "greek", "hungarian", "italian", "japanese", "koreana",
             "norwegian", "polish", "portuguese", "brazilian", "romanian", "russian", "spanish", "latam", "swedish", "thai", "turkish", "ukranian", "vietnamese", "all"]
lang_short = ["ar", "bg", "zh-CN", "zh-TW", "cs", "da", "nl", "en", "fi", "fr", "de", "el", "hu", "it", "ja",
              "ko", "no", "pl", "pt", "pt-BR", "ro", "ru", "es", "es-419", "sv", "th", "tr", "uk", "vn"]

language_dict = dict(zip(lang_short, lang_long))
filter_choices = ["recent", "updated", "all"]
review_type_choices = ["all", "positive", "negative"]
purchase_type_choices = ["all", "non_steam_purchase", "steam"]

parser = argparse.ArgumentParser(
    description="Retrieve reviews of an app on Steam", formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument_group(description="""
-f --filter         recent             – sorted by creation time
                    updated            – sorted by last updated time
                    all                – (default) sorted by helpfulness, with sliding windows based on day_range parameter, will always find results to return.
-l --language       see https://partner.steamgames.com/documentation/languages (and use the API language code list) or pass “all” for all reviews.
-d --day_range      range from now to n days ago to look for helpful reviews. Only applicable for the “all” filter.
-b --batches        reviews are returned in batches of 20 by default (change using num_per_page parameter). Specify the number of batches to return.
-r --review_type    all                – (default) all reviews
                    positive           – only positive reviews
                    negative           – only negative reviews
-p --purchase_type  all                – all reviews
                    non_steam_purchase – reviews written by users who did not pay for the product on Steam
                    steam              – reviews written by users who paid for the product on Steam (default)
-n --num_per_page   by default, up to 20 reviews will be returned. More reviews can be returned based on this parameter (with a maximum of 100 reviews)
-t --translate      if 1, all reviews will be translated to english (default 0)
--deepl_api_key     API key for deepl.com. Must be provided if translating
""")
parser.add_argument("app_id", type=str)
parser.add_argument("output_file", type=str)
parser.add_argument("-f", "--filter", dest="filter",
                    type=str, choices=filter_choices, default="all", help=argparse.SUPPRESS)
parser.add_argument("-l", "--language", dest="language", type=str,
                    default="all", choices=lang_long + lang_short, help=argparse.SUPPRESS)
parser.add_argument("-d", "--day_range",
                    dest="day_range", type=int, nargs=1, help=argparse.SUPPRESS)
parser.add_argument("-b", "--batches", dest="batches",
                    type=int, nargs=1, default=1, help=argparse.SUPPRESS)
parser.add_argument("-r", "--review_type", dest="review_type", type=str,
                    choices=review_type_choices, default="all", help=argparse.SUPPRESS)
parser.add_argument("-p", "--purchase_type", dest="purchase_type", type=str,
                    choices=purchase_type_choices, default="steam", help=argparse.SUPPRESS)
parser.add_argument("-n", "--num_per_page", dest="num_per_page",
                    type=int, choices=range(101), default=20, help=argparse.SUPPRESS)
parser.add_argument("-t", "--translate", dest="translate", type=bool,
                    choices=[True, False], default=False, help=argparse.SUPPRESS)
parser.add_argument("--deepl_api_key", dest="deepl_api_key",
                    type=str, help=argparse.SUPPRESS)

args = parser.parse_args()

# Use correct language format
if args.language in lang_short:
    language = language_dict.get(args.language)
else:
    language = args.language

# Base URL
url = "https://store.steampowered.com/appreviews/"
# Add App ID
url += F"{args.app_id}?json=1"
# Add filter
url += F"&filter={args.filter}"
# Add language
url += f"&language={language}"
# Add day range if given
if args.day_range is not None:
    url += f"&day_range={args.day_range}"
# Add review type
url += f"&review_type={args.review_type}"
# Add purchase type
url += f"&purchase_type={args.purchase_type}"
# Add num_per_page
url += f"&num_per_page={args.num_per_page}"
# Initial cursor
cursor = f"&cursor=*"

raw_review_list = []

if args.filter == "recent" or args.filter == "updated":
    reviews = True
    number_of_reviews = 0
    while reviews:
        print("Queried: " + url + cursor)
        resp = requests.get(url + cursor)
        data = json.loads(resp.content)
        number_of_reviews += data.get("query_summary").get("num_reviews")
        print(f"Number of reviews: {number_of_reviews}")

        if data.get("query_summary").get("num_reviews") == 0:
            reviews = False
        else:
            for item in data.get("reviews"):
                raw_review_list.append(item)
            new_cursor = data.get("cursor")
            cursor = f"&cursor={urllib.parse.quote(new_cursor)}"
else:
    print("Queried: " + url + cursor)
    resp = requests.get(url + cursor)
    data = json.loads(resp.content)
    number_of_reviews = data.get("query_summary").get("num_reviews")
    print(f"Number of reviews: {number_of_reviews}")

    for item in data.get("reviews"):
        raw_review_list.append(item)

review_list = []

for review in raw_review_list:
    # Add fields
    playtime = review.get("author").get("playtime_at_review")/60
    language = review.get("language")
    body = review.get("review")
    time_created = str(datetime.fromtimestamp(review.get("timestamp_created")))
    recommend = review.get("voted_up")
    weighted_vote_score = review.get("weighted_vote_score")

    # Add to list of reviews
    review_list.append({"playtime": playtime, "language": language, "body": body,
                       "time_created": time_created, "recommend": recommend, "weighted_vote_score": weighted_vote_score})

if args.translate:
    # Use DeepL API to translate any non-english comments
    import deepl
    if args.deepl_api_key == None:
        print("ERROR: A valid DeepL API key must be provided if translating!")
        exit()
    translator = deepl.Translator(args.deepl_api_key)

    # Find number of non-english reviews
    non_english = sum(x.get("language") != "english" for x in review_list)
    # Calculat total character usage
    total_characters = sum(len(x.get("body")) if x.get(
        "language") != "english" else 0 for x in review_list)
    print(
        f"Translating {non_english} reviews, total of {total_characters} characters")

    count = 0
    characters = 0
    for review in review_list:
        if review.get("language") != "english":
            count += 1
            characters += len(review.get("body"))
            print(
                f"Translating {count}/{non_english} reviews, {characters}/{total_characters} characters...")
            result = translator.translate_text(
                review.get("body"), target_lang="EN-GB")
            review["body"] = str(result)


# Output to CSV file
with open(args.output_file, "w", newline="", encoding="utf-8") as output_file:
    dict_writer = csv.DictWriter(output_file, review_list[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(review_list)
