from scrape_linkedin import Company, Profile
from os import path
import bs4
from bs4 import BeautifulSoup as BS
DIR = path.dirname(path.abspath(__file__))


def test_company_overview():
    expected_overview = {
        "name": "Facebook",
        "num_employees": 44632,
        "type": "Public Company",
        "company_size": "10,001+ employees",
        "specialties": "Connectivity, Artificial Intelligence, Virtual Reality, Machine Learning, Social Media, Augmented Reality, Marketing Science, Mobile Connectivity, and Open Compute",
        "founded": "2004",
        "industry": "Internet",
        "headquarters": "Menlo Park, CA",
        "website": "http://www.facebook.com/careers"
    }
    with open(path.join(DIR, 'html_files/facebook_overview.html'), 'r') as f:
        company = Company(f.read(), '', '').to_dict()
    for key in expected_overview:
        assert(expected_overview[key] == company['overview'][key])


def test_handles_full_html_page():
    """Ensure the full html page and the #profile-wrapper element
    given to the Profile constructor yield the same Profile object"""
    with open(path.join(DIR, 'html_files/profile.html'), 'r') as f:
        profile_html = f.read()
    profile = Profile(profile_html)
    print(profile.to_dict().keys())
    assert profile.personal_info['name'] == "Austin O'Boyle"
