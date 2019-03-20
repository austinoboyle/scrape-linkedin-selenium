"""
Usage: pylinkedin -u url
Options:
  --url : Url of the profile you want to scrape
  --user : username portion of the url (linkedin.com/in/USER)
  -a --attribute : Display only a specific attribute, display everything by default
  -i --input_file : Raw path to html of the profile you want to scrape
  -o --output_file : path of output file you want to write returned content to
  -h --help : Show this screen.
Examples:
pylinkedin -u https://www.linkedin.com/in/nadia-freitag-81173966 -a skills -o my_skills.json
"""

import click
from click import ClickException
from .ProfileScraper import ProfileScraper
from .CompanyScraper import CompanyScraper
from .Profile import Profile
from .utils import HEADLESS_OPTIONS
from pprint import pprint
import json
import os
from selenium.webdriver import Firefox
from selenium.webdriver import Chrome


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
    driver_options = {}
    if headless:
        driver_options = HEADLESS_OPTIONS
    if company:
        url = 'http://www.linkedin.com/company/' + company
    if user:
        url = 'http://www.linkedin.com/in/' + user
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
