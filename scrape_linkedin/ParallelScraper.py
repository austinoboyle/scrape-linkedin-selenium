from .CompanyScraper import CompanyScraper
from .ProfileScraper import ProfileScraper
from .ConnectionScraper import ConnectionScraper
from .utils import HEADLESS_OPTIONS, split_lists
from joblib import Parallel, delayed
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import math
import json
import shutil
import os


def scrape_in_parallel(
    scraper_type,
    items,
    output_file,
    num_instances,
    temp_dir='tmp_data',
    driver=Chrome,
    driver_options=HEADLESS_OPTIONS,
    **kwargs
):
    chunked_items = split_lists(items, num_instances)
    os.mkdir(temp_dir)
    Parallel(n_jobs=num_instances)(delayed(scrape_job)(
        scraper_type=scraper_type,
        output_file=temp_dir + '/{}.json'.format(i),
        items=chunked_items[i],
        driver=driver,
        driver_options=driver_options,
        **kwargs
    ) for i in range(num_instances))

    all_data = {}
    for i in range(num_instances):
        with open(temp_dir + '/{}.json'.format(i), 'r') as data:
            all_data.update(json.load(data))
    if output_file:
        with open(output_file, 'w') as out:
            json.dump(all_data, out)
    shutil.rmtree(temp_dir)
    return all_data


def scrape_job(scraper_type, items, output_file, **scraper_kwargs):
    scraper = scraper_type(**scraper_kwargs)
    data = {}
    for item in items:
        try:
            if scraper_type == CompanyScraper:
                data[item] = scraper.scrape(company=item).to_dict()
            elif scraper_type == ConnectionScraper:
                data[item] = scraper.scrape(user=item)
            else:
                data[item] = scraper.scrape(user=item).to_dict()
        except Exception as e:
            print("{} could not be scraped".format(item))
            print(e)
        with open(output_file, 'w') as out:
            json.dump(data, out)
