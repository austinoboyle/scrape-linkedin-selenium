from scrape_linkedin import Company
from os import path

DIRNAME = path.dirname(__file__)


def test_company_overview():
    expected_overview = {
        'location': 'Menlo Park, CA',
        'company_type': 'Public Company',
        'name': 'Facebook',
        'website': 'http://www.facebook.com/careers',
        'num_employees': 29293,
        'year_founded': '2004',
        'industry': 'Internet',
        'company_size': '10,001+ employees'
    }
    with open(path.join(DIRNAME, 'html_files/facebook_overview.html'), 'r') as f:
        company = Company(f.read(), '', '').to_dict()
    for key in expected_overview:
        assert(expected_overview[key] == company['overview'][key])
