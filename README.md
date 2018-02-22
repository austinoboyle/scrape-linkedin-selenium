# scrape_linkedin

## Introduction

`scrape_linkedin` is a python package to scrape all details from public LinkedIn profiles, turning the data into structured json.
 
#### Warning:
* LinkedIn has strong anti-scraping policies, they may blacklist ips making unauthenticated or unusual requests

## Installation

### Install with pip
Run `pip install git+git://github.com/austinoboyle/scrape-linkedin-selenium.git`

### Install from source
`git clone https://github.com/austinoboyle/scrape-linkedin-selenium.git`

Run `python setup.py install`

### Tests
Tests are (so far) only run on static html files.  One of which is a linkedin profile, the other is just used to test some utility functions.

## Using this package

### Setup
Because of Linkedin's anti-scraping measures, you must make your selenium browser look like an actual user.  To do this, you need to add the li_at cookie to the selenium session.  This is done one of two ways:

1. Set the LI_AT environment variable
	- `$ export LI_AT=YOUR_LI_AT_VALUE`
2. Pass the cookie as a parameter to the Parser object.
	>>> `with Parser(cookie='YOUR_LI_AT_VALUE') as parser:`

A cookie value passed directly to the Parser object will override your
environment variable if both are set.

### Command line
scrape_linkedin comes with a command line argument module `scrapeli` created using [click](http://click.pocoo.org/5/).

Options:

* --url : Full Url of the profile you want to scrape
* --user: www.linkedin.com/in/USER
* -a --attribute : return only a specific attribute (default: return all attributes)
* -i --input_file : Raw path to html file of the profile you want to scrape
* -o --output_file: Raw path to output file for structured json profile (just
prints results by default)
* -h --help : Show this screen.

Examples:

* Get Austin O'Boyle's profile info: `scrapeli --user=austinoboyle`
* Get only the skills of Austin O'Boyle: `scrapeli --user=austinoboyle -a skills`
* Parse stored html profile and save json output: `scrapeli -i /path/file.html -o output.json`

### Python Package

Two main classes

`Scraper` - wrapper for selenium webdriver with some useful methods for loading
dynamic linkedin content
    
    from scrape_linkedin import Scraper
    with Scraper() as scraper:
        profile = scraper.get_profile('http://www.linkedin.com/in/austinoboyle')
        print (profile.to_dict())

`Profile` - the class that has properties to access all information pulled from
a profile.  Also has a to_dict() method that returns all of the data as a dict

    with open('profile.html', 'r') as profile_file:
        profile = Profile(profile_file.read())
        
    print (profile.skills)
    # [{...} ,{...}, ...]
    print (profile.experiences)
    # {jobs: [...], volunteering: [...],...}
    print (profile.to_dict())
    # {personal_info: {...}, experiences: {...}, ...}

### Structure of the fields scraped

- personal_info
    - name
    - company
    - school
    - headline
    - followers
    - summary
- skills
- experiences
    - volunteering
    - jobs
    - education
- interests
- accomplishments
    - publications
    - cerfifications
    - patents
    - courses
    - projects
    - honors
    - test scores
    - languages
    - organizations


### Issues
Report bugs and feature requests [here](https://github.com/austinoboyle/scrape-linkedin-selenium/issues).