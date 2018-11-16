from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='scrape_linkedin',
      version="0.4.0",
      description='Selenium Scraper for Linkedin Profiles',
      long_description=readme(),
      author="Austin O'Boyle",
      author_email='hello@austinoboyle.com',
      license='MIT',
      url='https://github.com/austinoboyle/scrape-linkedin-selenium',
      packages=['scrape_linkedin'],
      entry_points={'console_scripts': [
          'scrapeli=scrape_linkedin.cli:scrape']},
      keywords='linkedin selenium scraper web scraping',
      #   include_package_data=True,
      #   package_data={'scraper': ['data/*.txt']},
      zip_safe=False,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3'
      ],
      install_requires=[
          'beautifulsoup4>=4.6.0',
          'bs4',
          'selenium',
          'click',
          'joblib'
      ]
      )
