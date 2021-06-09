import logging
import re
from datetime import datetime
from typing import List, Optional

import bs4
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
HEADLESS_OPTIONS = {'chrome_options': options}

logger = logging.getLogger(__name__)


def _find_element(driver, by):
    """Looks up an element using a Locator"""
    return driver.find_element(*by)


def flatten_list(l):
    return [item for sublist in l for item in sublist]


def split_lists(lst, num):
    k, m = divmod(len(lst), num)
    return [lst[i * k + min(i, m): (i+1) * k + min(i + 1, m)] for i in range(num)]


class TextChanged(object):
    def __init__(self, locator, text):
        self.locator = locator
        self.text = text

    def __call__(self, driver):
        actual_text = _find_element(driver, self.locator).text
        return actual_text != self.text


class AnyEC(object):
    def __init__(self, *args):
        self.ecs = args

    def __call__(self, driver):
        for fn in self.ecs:
            try:
                if fn(driver):
                    return True
            except:
                pass
        return False


def one_or_default(element: Optional[bs4.Tag], selector: str, default=None) -> Optional[bs4.Tag]:
    """Return the first found element with a given css selector

    Params:
        - element {beautifulsoup element}: element to be searched
        - selector {str}: css selector to search for
        - default {any}: default return value

    Returns:
        beautifulsoup element if match is found, otherwise return the default
    """
    try:
        el = element.select_one(selector)
        if not el:
            return default
        return element.select_one(selector)
    except Exception as e:
        return default


def text_or_default(element, selector, default=None):
    """Same as one_or_default, except it returns stripped text contents of the found element
    """
    try:
        return element.select_one(selector).get_text().strip()
    except Exception as e:
        return default


def all_or_default(element, selector, default=[]):
    """Get all matching elements for a css selector within an element

    Params:
        - element: beautifulsoup element to search
        - selector: str css selector to search for
        - default: default value if there is an error or no elements found

    Returns:
        {list}: list of all matching elements if any are found, otherwise return
        the default value
    """
    try:
        elements = element.select(selector)
        if len(elements) == 0:
            return default
        return element.select(selector)
    except Exception as e:
        return default


def get_info(element, mapping, default=None):
    """Turn beautifulsoup element and key->selector dict into a key->value dict

    Args:
        - element: A beautifulsoup element
        - mapping: a dictionary mapping key(str)->css selector(str)
        - default: The defauly value to be given for any key that has a css
        selector that matches no elements

    Returns:
        A dict mapping key to the text content of the first element that matched
        the css selector in the element.  If no matching element is found, the
        key's value will be the default param.
    """
    return {key: text_or_default(element, mapping[key], default=default) for key in mapping}


def get_job_info(job: Optional[bs4.Tag]) -> List[dict]:
    """
    Returns:
        list of dicts, each element containing the details of a job for some company:
           - job title
           - company
           - date_range
           - location
           - description
           - company link
    """
    def _get_company_url(job_element):
        company_link = one_or_default(
            job_element, 'a[data-control-name="background_details_company"]')

        if not company_link:
            logger.info("Could not find link to company.")
            return ''

        pattern = re.compile('^/company/.*?/$')
        if not hasattr(company_link, 'href') or not pattern.match(company_link['href']):
            logger.warning(
                "Found company link el: %s, but either the href format was unexpected, or the href didn't exist.", company_link)
            return ''
        else:
            return 'https://www.linkedin.com' + company_link['href']

    position_elements = all_or_default(
        job, '.pv-entity__role-details-container')

    company_url = _get_company_url(job)

    all_positions = []

    # Handle UI case where user has muttiple consec roles at same company
    if (position_elements):
        company = text_or_default(job,
                                  '.pv-entity__company-summary-info > h3 > span:nth-of-type(2)')
        positions = list(map(lambda pos: get_info(pos, {
            'title': '.pv-entity__summary-info-v2 > h3 > span:nth-of-type(2)',
            'date_range': '.pv-entity__date-range span:nth-of-type(2)',
            'location': '.pv-entity__location > span:nth-of-type(2)',
            'description': '.pv-entity__description'
        }), position_elements))
        for pos in positions:
            pos['company'] = company
            pos['li_company_url'] = company_url
            if pos['description'] is not None:
                pos['description'] = pos['description'].replace(
                    'See less\n', '').replace('... See more', '').strip()

            all_positions.append(pos)

    else:
        job_info = get_info(job, {
            'title': '.pv-entity__summary-info h3:nth-of-type(1)',
            'company': '.pv-entity__secondary-title',
            'date_range': '.pv-entity__date-range span:nth-of-type(2)',
            'location': '.pv-entity__location span:nth-of-type(2)',
            'description': '.pv-entity__description',
        })
        if job_info['description'] is not None:
            job_info['description'] = job_info['description'].replace(
                'See less\n', '').replace('... See more', '').strip()

        job_info['li_company_url'] = company_url
        all_positions.append(job_info)

    if all_positions:
        company = all_positions[0].get('company', "Unknown")
        job_title = all_positions[0].get('title', "Unknown")
        logger.debug(
            "Attempting to determine company URL from position: {company: %s, job_title: %s}", company, job_title)
        url = _get_company_url(job)
        for pos in all_positions:
            pos['li_company_url'] = url

    return all_positions


def get_school_info(school):
    """
    Returns:
        dict of school name, degree, grades, field_of_study, date_range, &
        extra-curricular activities
    """
    return get_info(school, {
        'name': '.pv-entity__school-name',
        'degree': '.pv-entity__degree-name span:nth-of-type(2)',
        'grades': '.pv-entity__grade span:nth-of-type(2)',
        'field_of_study': '.pv-entity__fos span:nth-of-type(2)',
        'date_range': '.pv-entity__dates span:nth-of-type(2)',
        'activities': '.activities-societies'
    })


def get_volunteer_info(exp):
    """
    Returns:
        dict of title, company, date_range, location, cause, & description
    """
    return get_info(exp, {
        'title': '.pv-entity__summary-info h3:nth-of-type(1)',
        'company': '.pv-entity__secondary-title',
        'date_range': '.pv-entity__date-range span:nth-of-type(2)',
        'location': '.pv-entity__location span:nth-of-type(2)',
        'cause': '.pv-entity__cause span:nth-of-type(2)',
        'description': '.pv-entity__description'
    })


def get_skill_info(skill):
    """
    Returns:
        dict of skill name and # of endorsements
    """
    return get_info(skill, {
        'name': '.pv-skill-category-entity__name',
        'endorsements': '.pv-skill-category-entity__endorsement-count'
    }, default=0)


# Takes a recommendation element and return a dict of relevant information.
def get_recommendation_details(rec):
    li_id_expr = re.compile(
        r'((?<=in\/).+(?=\/)|(?<=in\/).+)')  # re to get li id
    # re to get date of recommendation
    date_expr = re.compile(r'\w+ \d{1,2}, \d{4}, ')
    rec_dict = {
        'text': None,
        'date': None,
        'connection': {
            'relationship': None,
            'name': None,
            'li_id': None
        }
    }

    # remove See more and See less
    for text_link in all_or_default(rec, 'a[role="button"]'):
        text_link.decompose()
    for ellipsis in all_or_default(rec, '.lt-line-clamp__ellipsis'):
        ellipsis.decompose()

    text = text_or_default(rec, '.pv-recommendation-entity__highlights')
    rec_dict['text'] = text.replace('\n', '').replace('  ', '')

    recommender = one_or_default(rec, '.pv-recommendation-entity__member')
    if recommender:
        try:
            rec_dict['connection']['li_id'] = li_id_expr.search(
                recommender.attrs['href']).group()
        except AttributeError as e:
            pass

        recommender_detail = one_or_default(
            recommender, '.pv-recommendation-entity__detail')
        if recommender_detail:
            name = text_or_default(recommender, 'h3')
            rec_dict['connection']['name'] = name

            recommender_ps = recommender_detail.find_all('p', recursive=False)

            if len(recommender_ps) == 2:
                try:
                    recommender_meta = recommender_ps[-1]
                    recommender_meta = recommender_meta.get_text().strip()
                    match = date_expr.search(recommender_meta).group()
                    dt = datetime.strptime(match, '%B %d, %Y, ')
                    rec_dict['date'] = dt.strftime('%Y-%m-%d')
                    relationship = recommender_meta.split(match)[-1]
                    rec_dict['connection']['relationship'] = relationship
                except (ValueError, AttributeError) as e:
                    pass

    return rec_dict
