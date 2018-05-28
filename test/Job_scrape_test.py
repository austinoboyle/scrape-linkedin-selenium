from scrape_linkedin import Job
from scrape_linkedin import JobScraper
import os
from pprint import pprint
import json

def scrapeTest():
    job_id = '706203889'
    
    assert ('LI_AT' in os.environ),"Must set LI_AT environment variable"

    with JobScraper.JobScraper(cookie=str(os.getenv('LI_AT'))) as scraper:
        job = scraper.scrape(job_id=job_id)
    
    output = job.to_dict()
    pprint(output)

if __name__ == '__main__':
    scrapeTest()
