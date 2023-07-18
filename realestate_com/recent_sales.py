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


Run with `python -m realestate_com.recent_sales`

'''

# %%

import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup
import undetected_chromedriver as uc  # anti-bot selenium patch
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from utils import selenium_utils
from utils import sqlite_utils
from utils import plot_utils


def get_property_val(driver, text):
    '''
    Extracts the value of a property by searching for that string.
    '''
    element_tag = 'p'
    element = selenium_utils.find_sibling_by_text(driver, text, element_tag, element_tag)
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
        cr = selenium_utils.fluent_wait(driver, mark=(By.XPATH, "//p[@data-testid='number-pie']")).text
        cr = round(int(cr.replace('%', '')) * 0.01, 2)  # round floating point error
        profile['clearance rate'] = cr
    except TimeoutException:
        profile['clearance rate'] = None

    # get date last updated
    t = selenium_utils.fluent_wait(driver, mark=(By.XPATH, "//p[@data-testid='clearance-rate-updated']")).text
    t = t.replace('Updated ', '')[:-5]  # [-5] drops timezone info

    t = datetime.strptime(t, "%a %d %b %H:%M %p") \
                .replace(year=datetime.now().year)  # REA updated date excludes year

    profile['updated'] = t.date()  # keep date, drop time

    return profile


def profile_all_states(driver):
    home = 'https://www.realestate.com.au/auction-results/'
    states = ['nsw', 'vic', 'qld', 'sa', 'wa', 'nt', 'act', 'tas']

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

    d = profile_all_states(driver)
    df = munge_profile_output(d)

    # %% --- write
    sqlite_utils.write_recent_sales_to_db(df, check_last_updated=True)

    # # %% --- debugging
    # url = 'https://www.realestate.com.au/auction-results/nsw'
    # driver.get(url)

    # get_state_profile(driver)
    # get_property_val(driver, 'Sold at auction')

    # # %% --- check last appended
    # d = sqlite_utils.read_recent_sales()
    # d[d['updated'] == d['updated'].max()]

    # %% Plot

    plot_df = sqlite_utils.read_recent_sales()
    plot_utils.plot_recent_sales(plot_df, 'clearance_rate')


    # %% Close the driver
    driver.quit()

