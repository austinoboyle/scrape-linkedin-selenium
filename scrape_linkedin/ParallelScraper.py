from .Scraper import Scraper
from .utils import HEADLESS_OPTIONS, split_lists
from joblib import Parallel, delayed
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import math
import json
import shutil
import os


def scrape_in_parallel(
    users,
    output_file,
    num_instances,
    temp_dir='tmp_data',
    driver=Chrome,
    driver_options=HEADLESS_OPTIONS,
    **kwargs
):
    chunked_users = split_lists(users, num_instances)
    os.mkdir(temp_dir)
    Parallel(n_jobs=num_instances)(delayed(scrape_job)(
        output_file=temp_dir + '/{}.json'.format(i),
        users=chunked_users[i],
        driver=driver,
        driver_options=driver_options,
        **kwargs
    ) for i in range(num_instances))

    all_data = {}
    for i in range(num_instances):
        with open(temp_dir + '/{}.json'.format(i), 'r') as data:
            all_data = {**all_data, **json.load(data)}
    with open(output_file, 'w') as out:
        json.dump(all_data, out)
    shutil.rmtree(temp_dir)


def scrape_job(users, output_file, **scraper_kwargs):
    scraper = Scraper(**scraper_kwargs)
    data = {}
    for user in users:
        try:
            data[user] = scraper.scrape(user=user).to_dict()
        except Exception as e:
            print("{} could not be scraped".format(user))
            print(e)
        with open(output_file, 'w') as out:
            json.dump(data, out)
