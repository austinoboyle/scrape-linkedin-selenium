from scrape_linkedin import Job
from os import path
import bs4
from bs4 import BeautifulSoup as BS

DIR = path.dirname(path.abspath(__file__))

global job_html
with open(path.join(DIR, 'job.html'), 'r') as f:
    job_html = f.read()

def test_handles_full_html_page():
    job = Job.Job(job_html)
    main_job_soup = BS(job_html, 'html.parser').select_one(
        '#job-wrapper')
    job2 = Job(str(main_job_soup))
    assert job == job2

if __name__ == '__main__':
    test_handles_full_html_page()
