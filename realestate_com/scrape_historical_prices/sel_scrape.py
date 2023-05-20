'''
Scrapes historical trends from https://www.realestate.com.au/nsw/ultimo-2007/

Includes:
* Sale and rental price for:
    - median price for houses/units
    - 5 year (monthly) median price trend for houses/units
* Suburb sales summary:
    - no. houses available (past month)
    - no. houses sold (past 12 months)
    - median time on market (past 12 months)
    - no. buyers (past month)
    - current rental yield
* Suburb rental summary:
    - no. houses available (past month)
    - no. houses leased (past 12 months)
    - median time on market (past 12 months)
    - no. buyers (past month)

'''

# %%
import pandas as pd
import re
import json
import sqlite3
import itertools
from datetime import datetime

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup  


# from selenium import webdriver
# options = webdriver.ChromeOptions()
# options.add_argument("disable-blink-features=AutomationControlled")
# options.add_argument("--incognito")

import undetected_chromedriver as uc  # anti-bot selenium patch

from utils.selenium_utils import (
    fluent_wait,
    find_sibling_by_text
)

URL_ROOT = r'https://www.realestate.com.au/neighbourhoods/'


def get_sydney_suburbs_urls():
    regions = [
        'Central & Northern Sydney',
        'Southern & South Western Sydney',
        'Western Sydney & Blue Mountains']

    postcodes = pd.read_csv('postcodes-suburbs-regions.csv')
    postcodes = postcodes.query('Region == @regions').reset_index(drop=True)

    urls = [f'{URL_ROOT}{s.lower().replace(" ", "-")}-{p}-nsw'
            for p, s in zip(postcodes['Postcode'], postcodes['Suburb'])]

    return urls


def get_suburb_from_url(url):
    '''
    Returns the suburb name given by a realestate neighbourhood url.
    NOTE: an identical function has been implemented in get_suburb_driver()
    '''
    return re.match(r'.+?(?=-\d)', url.replace(URL_ROOT, '')).group(0)
# todo:
# implement a way to find url from suburb name


def get_suburb_driver(url):
    '''
    Returns selenium WebDriver object for a given url.
    '''
    suburb = (' ').join(url.split(r'/')[-1].split('-')[:-2])
    print(suburb)

    driver.get(url)

    return driver


def pull_payload(driver):
    '''
    Waits for the payload to be delivered and then scrapes the raw json.
    bs4 is used because it is (faster? easier?) here.
    '''
    payload_xpath = "//script[contains(.,'window.ArgonautExchange')]"
    fluent_wait(driver, condition='locate', mark=(By.XPATH, payload_xpath))

    soup = BeautifulSoup(driver.page_source, "html.parser")

    payload = [s.contents[0] for
                s in soup.findAll('script')
                if len(s.contents) == 1
                and 'window.ArgonautExchange' in s.contents[0]][0]

    return payload


def munge_payload(payload):
    '''
    Munges json payload into dict
    '''

    def d_recursive_del(d, key):
        '''
        Recursively deletes a given key from a dict and all nested values.
        Also handles dictionaries nested within lists.

        Usage:
        ------
        Parses the suburb summary json payload and remove the "__typename"
        key from all nested dicts for easier downstream processing.
        '''
        if type(d) is list:
            return [d_recursive_del(element, key) for element in d]
        elif type(d) is dict:
            return {k: d_recursive_del(v, key) for k, v in d.items() if k != key}
        else:
            return d

    payload = json.loads(payload \
        .replace('window.ArgonautExchange=', '') \
        .replace('\\', '') \
        .replace(';', '') \
        .replace('"{', '{') \
        .replace('}}"}}', '}}}}'))
    
    payload = payload["resi-property_market-explorer"] \
                     ["suburb_data"] \
                     ["marketProfileBySlug"] \
                     ["insights"]

    return d_recursive_del(payload, '__typename')


def scrape_suburb_data(url):
    '''
    Simple wrapper to combine multiple functions
    '''
    driver = get_suburb_driver(url)
    payload = pull_payload(driver)
    d = munge_payload(payload)

    return d


def flatten_json(d, keys=[], flattened=[]):
    '''
    Takes a json and returns it as a list so it can be converted to
    table format and written into a database.

    Parameters:
    -----------
    d: the dictionary to flatten
    keys: unused arg to pass down recursive variables
    flattened: unused arg to pass down recursive variables

    Example:
    --------
    In: {'buy': {'house': {'allBed': {'yearly': {'value': 47}},
                'twoBed': {'yearly': {'value': 44}},
                'threeBed': {'yearly': {'value': 225}}},
            'rent': {'house': {'allBed': {'yearly': {'value': 21}},
                'twoBed': {'yearly': {'value': 20}},
                'threeBed': {'yearly': {'value': 26}}}
        }

    Out: [['buy', 'house', 'allBed', 'yearly', 'value', 47],
        ['buy', 'house', 'twoBed', 'yearly', 'value', 44],
        ['buy', 'house', 'threeBed', 'yearly', 'value', 225],
        ['rent', 'house', 'allBed', 'yearly', 'value', 21],
        ['rent', 'house', 'twoBed', 'yearly', 'value', 20],
        ['rent', 'house', 'threeBed', 'yearly', 'value', 26],
        ]
    '''

    for k, v in d.items():
        new_keys = [*keys, k]
        if isinstance(v, dict):
            flatten_json(v, new_keys)
        else:
            # print([*new_keys, v])
            flattened += [[*new_keys, v]]
            new_keys = new_keys[:-1]

    return flattened


driver = uc.Chrome()

# broken = []
# for url in urls:
#     d = scrape_suburb_data(url)

# --- debugging
url = urls[12]
d = scrape_suburb_data(url)

# %%

''' payload keys:
>>> payload
    ["resi-property_market-explorer"]
        ["suburb_data"]
            ["marketProfileBySlug"]
                ["insights"].keys()

<measure>: <description>
    {example payload}
----------------------------------
'medianPrice': yearly: latest summary data (median over past 12mths)
               trends: chart data (median price and volume over past 12 mths)
    {'yearly': ['display', 'volume']  # NOTE: redundant: equal to last trend element
     'trends': ['value', 'volume'] }  # list of dicts

'transactionVolume': number sold in the past 12 months
    "buy": {
      "house": {
        "allBed": {
          "yearly": {
            "value": 10

'daysOnSite': median time on market
    "buy": {
      "house": {
        "allBed": {
          "yearly": {
            "value": 47

'rentalYield': rental yield (only applies to "Buy" toggle)
    "house": {
      "allBed": {
        "yearly": {
          "display": "2.7%"


'supplyDemand': supply: properties available in the past month
                demand: interested buyers in the past 12 months
                # NOTE: 2 value keys
    "buy": {
      "house": {
        "allBed": {
          "monthly": {
            "supply": 5,
            "demand": 688

'''

output = []
measures = {
    'medianPrice': [],
    'transactionVolume': [],
    'daysOnSite': [],
    'rentalYield': [],
    'supplyDemand': [],
}

for m in measures:
    # if m == 'medianPrice':
    #     pass
    # else:
    #     try:
    #         output += [pd.DataFrame(flatten_json(d[m]))]
    #     except:
    #         print(m)

    print(m)
    display(pd.DataFrame(flatten_json(d[m])).head())
# %%

pd.concat(output, axis=0)
