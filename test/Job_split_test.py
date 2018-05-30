from scrape_linkedin import SplitViewJobScraper
import os
from pprint import pprint
import json

def scrapeTest():
    location = 'Kingston%2C%20Ontario%2C%20Canada'

    assert ('LI_AT' in os.environ),"Must set LI_AT environment variable"

    with SplitViewJobScraper.SplitViewJobScraper(cookie=str(os.getenv('LI_AT'))) as scraper:
        output = scraper.scrape_by_page(location=location,n=2)

    for job in output[0]:
        pprint(job.to_dict())

if __name__ == '__main__':
    scrapeTest()
