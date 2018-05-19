# scrape_linkedin

## Introduction

`scrape_linkedin` is a python package to scrape all details from public LinkedIn
profiles, turning the data into structured json.

**Warning**: LinkedIn has strong anti-scraping policies, they may blacklist ips making
unauthenticated or unusual requests

## Table of Contents

<!--ts-->

*   [scrape_linkedin](#scrape_linkedin)
    *   [Introduction](#introduction)
    *   [Table of Contents](#table-of-contents)
    *   [Installation](#installation)
        *   [Install with pip](#install-with-pip)
        *   [Install from source](#install-from-source)
        *   [Tests](#tests)
    *   [Getting &amp; Setting LI_AT](#getting--setting-li_at)
        *   [Getting LI_AT](#getting-li_at)
        *   [Setting LI_AT](#setting-li_at)
    *   [Usage](#usage)
        *   [Command Line](#command-line)
        *   [Python Package](#python-package)
            *   [Profiles](#profiles)
            *   [Companies](#companies)
    *   [Scraping in Parallel](#scraping-in-parallel)
        *   [Example](#example)
        *   [Configuration](#configuration)
    *   [Issues](#issues)

<!-- Added by: austinoboyle, at: 2018-05-06T20:13-04:00 -->

<!--te-->

## Installation

### Install with pip

Run `pip install git+git://github.com/austinoboyle/scrape-linkedin-selenium.git`

### Install from source

`git clone https://github.com/austinoboyle/scrape-linkedin-selenium.git`

Run `python setup.py install`

### Tests

Tests are (so far) only run on static html files. One of which is a linkedin
profile, the other is just used to test some utility functions.

## Getting & Setting LI_AT

Because of Linkedin's anti-scraping measures, you must make your selenium
browser look like an actual user. To do this, you need to add the li_at cookie
to the selenium session.

### Getting LI_AT

1.  Navigate to www.linkedin.com and log in
2.  Open browser developer tools (Ctrl-Shift-I or right click -> inspect
    element)
3.  Select the appropriate tab for your browser (**Application** on Chrome,
    **Storage** on Firefox)
4.  Click the **Cookies** dropdown on the left-hand menu, and select the
    `www.linkedin.com` option
5.  Find and copy the li_at **value**

### Setting LI_AT

There are two ways to set your li_at cookie:

1.  Set the LI_AT environment variable
    *   `$ export LI_AT=YOUR_LI_AT_VALUE`
    *   **On Windows**: `$ set LI_AT=YOUR_LI_AT_VALUE
2.  Pass the cookie as a parameter to the Parser object.
    > `>>> with Scraper(cookie='YOUR_LI_AT_VALUE') as scraper:`

A cookie value passed directly to the Parser object **will override your
environment variable** if both are set.

## Usage

### Command Line

scrape_linkedin comes with a command line argument module `scrapeli` created
using [click](http://click.pocoo.org/5/).

**Note: CLI only works with Personal Profiles as of now.**

Options:

*   --url : Full Url of the profile you want to scrape
*   --user: www.linkedin.com/in/USER
*   -a --attribute : return only a specific attribute (default: return all
    attributes)
*   -i --input_file : Raw path to html file of the profile you want to scrape
*   -o --output_file: Raw path to output file for structured json profile (just
    prints results by default)
*   -h --help : Show this screen.

Examples:

*   Get Austin O'Boyle's profile info: `$ scrapeli --user=austinoboyle`
*   Get only the skills of Austin O'Boyle: `$ scrapeli --user=austinoboyle -a skills`
*   Parse stored html profile and save json output: `$ scrapeli -i /path/file.html -o output.json`

### Python Package

#### Profiles

`ProfileScraper` - wrapper for selenium webdriver with some useful methods for loading
dynamic linkedin content

```python
from scrape_linkedin import ProfileScraper

with ProfileScraper() as scraper:
    profile = scraper.scrape(user='austinoboyle')
print(profile.to_dict())
```

`Profile` - the class that has properties to access all information pulled from
a profile. Also has a to_dict() method that returns all of the data as a dict

    with open('profile.html', 'r') as profile_file:
        profile = Profile(profile_file.read())

    print (profile.skills)
    # [{...} ,{...}, ...]
    print (profile.experiences)
    # {jobs: [...], volunteering: [...],...}
    print (profile.to_dict())
    # {personal_info: {...}, experiences: {...}, ...}

**Structure of the fields scraped**

*   personal_info
    *   name
    *   company
    *   school
    *   headline
    *   followers
    *   summary
*   skills
*   experiences
    *   volunteering
    *   jobs
    *   education
*   interests
*   accomplishments
    *   publications
    *   cerfifications
    *   patents
    *   courses
    *   projects
    *   honors
    *   test scores
    *   languages
    *   organizations

#### Companies

```python
from scrape_linkedin import ProfileScraper

with ProfileScraper() as scraper:
    profile = scraper.scrape(user='austinoboyle')
print(profile.to_dict())
```

`Profile` - the class that has properties to access all information pulled from
a profile. Also has a to_dict() method that returns all of the data as a dict

    with open('profile.html', 'r') as profile_file:
        profile = Profile(profile_file.read())

    print (profile.skills)
    # [{...} ,{...}, ...]
    print (profile.experiences)
    # {jobs: [...], volunteering: [...],...}
    print (profile.to_dict())
    # {personal_info: {...}, experiences: {...}, ...}

**Structure of the fields scraped**

*   overview
    *   name
    *   industry
    *   description
    *   location
    *   website
    *   year_founded
    *   company_type
    *   company_size
    *   num_employees
*   jobs
*   life

## Scraping in Parallel

New in version 0.2: built in parallel scraping functionality. Note that the
up-front cost of starting a browser session is high, so in order for this to be
beneficial, you will want to be scraping many (> 15) profiles.

### Example

```python
from scrape_linkedin import scrape_in_parallel

users = ['austinoboyle', 'joeblow', 'another_linkedin_user', ...]

#Scrape all profiles, output to 'data.json' file, use 4 browser instances
scrape_in_parallel(users=users, output_file="data.json", num_instances=4)
```

### Configuration

**Parameters:**

*   _users_ **`{list}`**: List of usernames to be scraped
*   _output_file_ **`{str}`**: path to output file
*   _num_instances_ **`{int}`**: number of parallel instances of selenium to run
*   _temp_dir_ **`{str}`**: name of temporary directory to use to store data from intermediate steps
    *   **default: 'tmp_data'**
*   _driver_ {selenium.webdriver}: driver to use for scraping
    *   **default: selenium.webdriver.Chrome**
*   _driver_options_ **`{dict}`**: dict of keyword arguments to pass to the driver function.
    *   **default: scrape_linkedin.utils.HEADLESS_OPTIONS**
*   _\*\*kwargs_ **`{any}`**: keyword arguments to pass to the scrape_linkedin.Scraper constructor for each job

## Issues

Report bugs and feature requests
[here](https://github.com/austinoboyle/scrape-linkedin-selenium/issues).
