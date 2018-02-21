"""
Usage: pylinkedin -u url
Options:
  -u --url : Url of the profile you want to scrape
  -a --attribute : Display only a specific attribute, display everything by default
  -f --file_path : Raw path to html of the profile you want to scrape
  -o --output_path : path of output file you want to write returned content to
  -h --help : Show this screen.
Examples:
pylinkedin -u https://www.linkedin.com/in/nadia-freitag-81173966 -a skills -o my_skills.json
"""

import click
from click import ClickException
from .Scraper import Scraper
from .Profile import Profile
from pprint import pprint
import json
import os


@click.command()
@click.option('--url', type=str, help='Url of the profile you want to scrape')
@click.option('--user', type=str, help='Username portion of profile: (www.linkedin.com/in/<username>')
@click.option('--attribute', '-a', type=click.Choice(Profile.attributes))
@click.option('--file_path', '-f', type=click.Path(exists=True), default=None, help='Path to html of the profile you wish to load')
@click.option('--output_path', '-o', type=click.Path(), default=None, help='Output file you want to write returned content to')
def scrape(url, user, attribute, file_path, output_path):
    if user:
        url = 'http://www.linkedin.com/in/' + user
    if (url and file_path) or (not url and not file_path):
        raise ClickException(
            'Must pass either a url or file path, but not both.')
    elif url:
        if 'LI_AT' not in os.environ:
            raise ClickException("Must set LI_AT environment variable")
        with Scraper(cookie=os.environ['LI_AT']) as scraper:
            profile = scraper.get_profile(url)
    else:
        with open(file_path, 'r') as html:
            profile = Profile(html)

    if attribute:
        output = profile.__getattribute__(attribute)
    else:
        output = profile.to_dict()

    if output_path:
        with open(output_path, 'w') as outfile:
            json.dump(output, outfile)
    else:
        pprint(output)


if __name__ == '__main__':
    scrape()
