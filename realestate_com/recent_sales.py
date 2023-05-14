'''
Scrapes realestate.com.au for Recent Sales results, i.e. properties:
    Sold at auction
    Sold prior to auction
    Sold after auction
    Withdrawn
    Passed in
    Private sales

Note: 
* undetected_chromedriver requires Chrome to be updated to the latest version

'''

# %%

import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup

import undetected_chromedriver as uc  # anti-bot selenium patch
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from utils.selenium_utils import (
    fluent_wait,
    find_sibling_by_text
)
from utils.sqlite_utils import write_recent_sales_to_db


def get_property_val(driver, text):
    '''
    Extracts the value of a property by searching for that string.
    '''
    element_tag = 'p'
    element = find_sibling_by_text(driver, text, element_tag, element_tag)
    val = int(element.text.replace(',', ''))  # handle thousands comma

    return val


def get_state_profile(driver):
    '''
    Parses latest auction and sales results.

    Todo:
    * parse domain.com (www.domain.com.au/auction-results/sydney)

    '''

    properties = [
        'Sold at auction',
        'Sold prior to auction',
        'Sold after auction',
        'Withdrawn',
        'Passed in',
        'Private sales'
    ]

    profile = {p: get_property_val(driver, p)
               for p in properties}

    # get clearance rate
    try:  # NA when no houses are auctioned (fluent_wait will timeout)
        cr = fluent_wait(driver, By.XPATH, "//p[@data-testid='number-pie']").text
        cr = round(int(cr.replace('%', '')) * 0.01, 2)  # round floating point error
        profile['clearance rate'] = cr
    except TimeoutException:
        profile['clearance rate'] = None

    # get date last updated
    t = fluent_wait(driver, By.XPATH, "//p[@data-testid='clearance-rate-updated']").text
    t = t.replace('Updated ', '')[:-5]  # [-5] drops timezone info

    t = datetime.strptime(t, "%a %d %b %H:%M %p") \
                .replace(year=datetime.now().year)  # REA updated date excludes year

    profile['updated'] = t.date()  # keep date, drop time

    return profile


def profile_all_states(driver):
    home = 'https://www.realestate.com.au/auction-results/'
    states = ['nsw', 'qld', 'sa', 'wa', 'nt', 'act', 'tas']

    output = {}

    print('Profiling ', end='')
    for s in states:
        print(s, end=', ')
        url = home + s
        driver.get(url)

        d = get_state_profile(driver=driver)

        output[s] = d

    print('done')

    return output


def munge_profile_output(d):
    '''
    Processes recent sales results and returns a pandas df.
    '''

    df = pd.DataFrame(d).T

    df.index.name = 'state'
    df = df.reset_index()
    df.columns = [i.lower().replace(' ', '_') for i in df.columns]

    df['queried'] = datetime.today().date()

    return df


def scrape_suburb_sales():
    # WIP

    # get suburb links 
    # bs4 seems faster than selenium)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    suburb_links = [f"https://www.realestate.com.au{l['href']}"
                    for l in soup.find_all('a', href=True)
                    if '/auction-results/' in l['href']][1:]

    suburb_links

    return


if __name__ == "__main__":
    driver = uc.Chrome()
    driver.minimize_window()

    d = profile_all_states(driver)
    df = munge_profile_output(d)

    # %% --- write
    write_recent_sales_to_db(df)

    # %% --- debugging
    url = 'https://www.realestate.com.au/auction-results/nsw'
    driver.get(url)

    get_state_profile(driver)

    get_property_val(driver, 'Sold at auction')

    # %% Close the driver
    driver.quit()

