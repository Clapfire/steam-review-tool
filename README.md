# Terminal Tool for Getting Steam Reviews (And Translating)

A simple terminal python script for getting a list of reviews of an app on Steam, optionally translating non-english reviews and creating a csv file with:

- Playtime
- Review Text
- Upvoted
- Weighted Review Score
- Timestamp

Note that translation is performed using DeepL, so an API key from there must be provided.

## Usage

usage: python GetSteamReviews.py [-h] app_id output_file

positional arguments:
app_id
output_file

optional arguments:
-h, --help show this help message and exit

-f --filter

    recent             – sorted by creation time
    updated            – sorted by last updated time
    all                – (default) sorted by helpfulness,
                        with sliding windows based on day_range parameter,
                        will always find results to return.

-l --language

    see https://partner.steamgames.com/documentation/languages (and use the API language code list) or pass “all” for all reviews.

-d --day_range

    range from now to n days ago to look for helpful reviews. Only applicable for the “all” filter.

-b --batches

    reviews are returned in batches of 20 by default (change using num_per_page parameter). Specify the number of batches to return.

-r --review_type

    all                – (default) all reviews
    positive           – only positive reviews
    negative           – only negative reviews

-p --purchase_type

    all                – all reviews
    non_steam_purchase – reviews written by users who did not pay for the product on Steam
    steam              – reviews written by users who paid for the product on Steam (default)

-n --num_per_page

    by default, up to 20 reviews will be returned. More reviews can be returned based on this parameter (with a maximum of 100 reviews)

-t --translate

    if true(1), all reviews will be translated to english using the DeepL API (default false(0))

--deepl_api_key

    API key for deepl.com. Must be provided if translating
