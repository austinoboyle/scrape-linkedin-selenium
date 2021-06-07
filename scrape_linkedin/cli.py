"""
Usage: scrapeli -u url
Options:
  --url : Url of the profile you want to scrape
  --user : username portion of the url (linkedin.com/in/USER)
  -a --attribute : Display only a specific attribute, display everything by default
  -i --input_file : Raw path to html of the profile you want to scrape
  -o --output_file : path of output file you want to write returned content to
  -h --help : Show this screen.
Examples:
scrapeli -u https://www.linkedin.com/in/austinoboyle -a skills -o my_skills.json
"""

import datetime
import json
import logging
import os
from pprint import pprint

import click
from click import ClickException
from selenium.webdriver import Chrome, Firefox

from .CompanyScraper import CompanyScraper
from .Profile import Profile
from .ProfileScraper import ProfileScraper
from .utils import HEADLESS_OPTIONS

logger = logging.getLogger(__name__)


def _init_logging():
    now_time_str = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # Set the default logging level for all other modules to WARNING
    log_fname = 'scrapeli_{}.log'.format(now_time_str)
    print("Logging debug information to", log_fname)
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(levelname)-8s %(name)s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        filename=log_fname,
                        filemode='w')
    # Set our internal log level to DEBUG
    logging.getLogger('scrape_linkedin').setLevel(logging.DEBUG)


@click.command()
@click.option('--url', type=str, help='Url of the profile you want to scrape')
@click.option('--user', type=str, help='Username portion of profile: (www.linkedin.com/in/<username>')
@click.option('--company', type=str, help='ID of Company you want to scrape. (https://www.linkedin.com/company/id/)')
@click.option('--attribute', '-a', type=click.Choice(Profile.attributes))
@click.option('--input_file', '-i', type=click.Path(exists=True), default=None,
              help='Path to html of the profile you wish to load')
@click.option('--headless', is_flag=True, help="Run in headless mode")
@click.option('--output_file', '-o', type=click.Path(), default=None,
              help='Output file you want to write returned content to')
@click.option('--driver', type=click.Choice(['Chrome', 'Firefox']), help='Webdriver to use: (Firefox/Chrome)', default='Chrome')
def scrape(url, user, company, attribute, input_file, headless, output_file, driver):
    _init_logging()
    driver_options = {}
    logger.debug("CLI Initialized")
    if headless:
        logger.debug("HEADLESS")
        driver_options = HEADLESS_OPTIONS
    if company:
        url = 'https://www.linkedin.com/company/' + company
    if user:
        url = 'https://www.linkedin.com/in/' + user
    if (url and input_file) or (not url and not input_file):
        raise ClickException(
            'Must pass either a url or file path, but not both.')
    elif url:
        if 'LI_AT' not in os.environ:
            raise ClickException("Must set LI_AT environment variable")
        driver_type = Firefox if driver == 'Firefox' else Chrome
        if company:
            with CompanyScraper(driver=driver_type, cookie=os.environ['LI_AT'], driver_options=driver_options) as scraper:
                profile = scraper.scrape(company=company)
        else:
            with ProfileScraper(driver=driver_type, cookie=os.environ['LI_AT'], driver_options=driver_options) as scraper:
                profile = scraper.scrape(url=url)

    else:
        with open(input_file, 'r') as html:
            profile = Profile(html)

    if attribute:
        output = profile.__getattribute__(attribute)
    else:
        output = profile.to_dict()

    if output_file:
        with open(output_file, 'w') as outfile:
            json.dump(output, outfile)
    else:
        pprint(output)


if __name__ == '__main__':
    scrape()
