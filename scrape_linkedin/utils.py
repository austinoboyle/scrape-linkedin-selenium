from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.expected_conditions import _find_element

import math

options = Options()
options.add_argument('--headless')
HEADLESS_OPTIONS = {'chrome_options': options}


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


def one_or_default(element, selector, default=None):
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


def get_job_info(job):
    """
    Returns:
        dict of job's title, company, date_range, location, description
    """
    multiple_positions = all_or_default(
        job, '.pv-entity__role-details-container')

    # Handle UI case where user has muttiple consec roles at same company
    if (multiple_positions):
        company = text_or_default(job,
                                  '.pv-entity__company-summary-info > h3 > span:nth-of-type(2)')
        multiple_positions = list(map(lambda pos: get_info(pos, {
            'title': '.pv-entity__summary-info-v2 > h3 > span:nth-of-type(2)',
            'date_range': '.pv-entity__date-range span:nth-of-type(2)',
            'location': '.pv-entity__location > span:nth-of-type(2)',
            'description': '.pv-entity__description'
        }), multiple_positions))
        for pos in multiple_positions:
            pos['company'] = company
        return multiple_positions

    else:
        return [get_info(job, {
            'title': '.pv-entity__summary-info h3:nth-of-type(1)',
            'company': '.pv-entity__secondary-title',
            'date_range': '.pv-entity__date-range span:nth-of-type(2)',
            'location': '.pv-entity__location span:nth-of-type(2)',
            'description': '.pv-entity__description'
        })]


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
