from scrape_linkedin import Profile
from os import path
import bs4
from bs4 import BeautifulSoup as BS
DIR = path.dirname(path.abspath(__file__))


with open(path.join(DIR, 'profile.html'), 'r') as f:
    profile_html = f.read()
global profile_html


def test_handles_full_html_page():
    """Ensure the full html page and the #profile-wrapper element
    given to the Profile constructor yield the same Profile object"""

    profile = Profile(profile_html)
    assert profile.personal_info['name'] == "Austin O'Boyle"
    main_profile_soup = BS(profile_html, 'html.parser').select_one(
        '#profile-wrapper')
    profile2 = Profile(str(main_profile_soup))
    assert profile == profile2
