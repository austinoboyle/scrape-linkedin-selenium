from scrape_linkedin import scrape_in_parallel, Scraper
from scrape_linkedin.utils import HEADLESS_OPTIONS
import time
import json
import sys
import os


def test_parallel():
    users = ['austinoboyle', 'seancahalan', 'alexandre-granzer-guay-8b8378b2',
             'nicole-odenwald-45989594', 'swishgoswami', 'tang-david',
             'y-hung-tam-3943a636', 'delaramayazdi'
             ]
    with open('hrefs.json', 'r') as user_data:
        users = json.load(user_data)[0:8]
    data = {}
    scraper = Scraper(driver_options=HEADLESS_OPTIONS)
    for user in users:
        data[user] = scraper.scrape(user=user).to_dict()
    with open('../out2.json', 'w') as out:
        json.dump(data, out)


if __name__ == '__main__':
    test_parallel()
