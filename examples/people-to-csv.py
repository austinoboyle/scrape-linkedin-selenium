"""Example to scrape a list of Companies, and put overviews in csv form"""

from scrape_linkedin import CompanyScraper
import pandas as pd

# LIST YOUR COMPANIES HERE
my_company_list = [
    'facebook', 'mit-sloan-school-of-management', 'linkedin',
    'harvard-university'
]

company_data = []

with CompanyScraper() as scraper:
    # Get each company's overview, add to company_data list
    for name in my_company_list:
        sc = scraper.scrape(company=name, people=True)
        overview = sc.overview
        overview['company_name'] = name
        overview['people'] = sc.people
        company_data.append(overview)

# Turn into dataframe for easy csv output
df = pd.DataFrame(company_data)
df.to_csv('out.csv', index=False)
