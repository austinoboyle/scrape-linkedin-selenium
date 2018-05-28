from scrape_linkedin import JobSearchScraper
import os
from pprint import pprint
import json

def scrapeTest():
    location = 'Kingston%2C%20Ontario%2C%20Canada'

    assert ('LI_AT' in os.environ),"Must set LI_AT environment variable"

    with JobSearchScraper.JobSearchScraper(cookie=str(os.getenv('LI_AT'))) as scraper:
        output = scraper.scrape(location=location)

    for job in output:
        pprint(job.to_dict())

if __name__ == '__main__':
    scrapeTest()
