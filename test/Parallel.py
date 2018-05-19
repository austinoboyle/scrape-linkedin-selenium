from scrape_linkedin import scrape_in_parallel, ProfileScraper, CompanyScraper
from scrape_linkedin.utils import HEADLESS_OPTIONS
import time
import json
import sys
import os


def parallel():
    companies = ['google', 'facebook']
    scrape_in_parallel(scraper_type=CompanyScraper, items=companies,
                       output_file='companies.json', num_instances=2)


if __name__ == '__main__':
    parallel()
