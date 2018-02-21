from scrape_linkedin import utils as u
import bs4
from bs4 import BeautifulSoup as BS
from os import path

file_path = path.abspath(__file__)
DIR = path.dirname(file_path)

with open(path.join(DIR, 'profile.html'), 'r') as f1, open(path.join(DIR, 'test.html'), 'r') as f2:
    profile_soup = BS(f1.read(), 'html.parser')
    basic_soup = BS(f2.read(), 'html.parser')

global profile_soup
global basic_soup


def test_all_or_default():
    assert u.all_or_default(profile_soup, '.asjdksjaldjsklajdksaldas') == []
    assert u.all_or_default(
        profile_soup, '.fjdskalfjdsalfs', default=None) == None
    assert len(u.all_or_default(profile_soup, '.pv-profile-section')) == 22

    assert u.all_or_default(None, '.test1') == []


def test_text_or_default():
    assert u.text_or_default(basic_soup, '.asdf') == None
    assert u.text_or_default(basic_soup, '.test1') == 'Test'


def test_one_or_default():
    el = u.one_or_default(basic_soup, '.test1')
    assert isinstance(el, bs4.element.Tag)
    el = u.one_or_default(basic_soup, '.asdfgh', default='')
    assert el == ''


def test_get_info():
    mapping = {
        'name': '.test1',
        'value': '.asdfg'
    }
    default = None
    output = u.get_info(basic_soup, mapping)
    expected_output = {}
    for key, selector in mapping.items():
        expected_output[key] = u.text_or_default(
            basic_soup, selector, default=default)
    assert output == expected_output
