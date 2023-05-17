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

import time

# from selenium import webdriver
# options = webdriver.ChromeOptions()
# options.add_argument("disable-blink-features=AutomationControlled")
# options.add_argument("--incognito")

import undetected_chromedriver as uc  # anti-bot selenium patch

from utils.selenium_utils import (
    fluent_wait,
    find_sibling_by_text
)


def get_suburb_from_url(url):
    '''
    Returns the suburb name given by a realestate neighbourhood url.
    NOTE: an identical function has been implemented in get_suburb_driver()
    '''
    return re.match(r'.+?(?=-\d)', url.replace(url_base, '')).group(0)
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


def get_suburb_payload(driver):
    '''
    Parses current page html to find json payload and munge into dict
    '''

    fluent_wait(driver, condition='locate',
                mark=(By.XPATH, "/html/body/script"))

    soup = BeautifulSoup(driver.page_source, "html.parser")

    payload = [s.contents[0] for
            s in soup.findAll('script')
            if len(s.contents) == 1
            and 'window.ArgonautExchange' in s.contents[0]][0]

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


def d_recursive_del(d, key):
    '''
    Recursively deletes a given key from a dictionary and all nested values.
    Also handles dictionaries nested within lists.

    Used to parse the json payload containing suburb summary data and remove
    the "__typename" key from all nested dicts.
    '''
    if type(d) is list:
        return [d_recursive_del(element, key) for element in d]
    elif type(d) is dict:
        return {k: d_recursive_del(v, key) for k, v in d.items() if k != key}
    else:
        return d


# # 2br/3br/4br
# brs = {
#     'median_2br': 'left',
#     'median_3br': 'middle',
#     'median_4br': 'right'
# }


# dummy = {
#     'house_buy': {
#         'median': 'price',
#         'median_2br': 'median_2br',
#         'median_3br': 'median_3br',
#         'median_4br': 'median_4br',
#         'updated': 'date'
#     },
#     'house_rent': {
#         'median': 'price',
#         'median_2br': 'median_2br',
#         'median_3br': 'median_3br',
#         'median_4br': 'median_4br',
#         'updated': 'date'
#     },
#     'unit_buy': {
#         'median': 'price',
#         'median_2br': 'median_2br',
#         'median_3br': 'median_3br',
#         'median_4br': 'median_4br',
#         'updated': 'date'
#     },
#     'unit_rent': {
#         'median': 'price',
#         'median_2br': 'median_2br',
#         'median_3br': 'median_3br',
#         'median_4br': 'median_4br',
#         'updated': 'date'
#     }
# }


# def scrape_element(element):
#     '''Returns a dict of all data for a given web element (price subsection)'''

#     d = {
#         'median': '',
#         'median_2br': '',
#         'median_3br': '',
#         'median_4br': '',
#         'updated': ''
#     }

#     price = element.find_element_by_xpath(".//div[@class='price h1 strong']").text
#     price = re.sub('[$, PW]', '', price)

#     if price != 'nodata':
#         date = element.find_element_by_xpath(f".//div[@class='processed-date p-small']"
#                                 f"//span[@class='strong']").text
#         d['updated'] = pd.to_datetime(date).strftime('%Y-%m-%d')
#         d['median'] = int(price)

#         # 2br/3br/4br
#         for k, v in brs.items():
#             price = element.find_element_by_xpath(f".//a[@class='breakdown-subsection {v}-subsection']" 
#                                             f"//div[@class='price strong']").text
#             price = re.sub('[$, PW-]', '', price)
#             if price == '':
#                 price = 0
#             d[k] = int(price)

#     return d

# def scrape_trend_data(driver):
#     trend_element = driver.find_element_by_xpath("//div[@class='slide-section median-price-subsections trend']")
#     trend_data = trend_element.get_attribute('data-trend')

#     d = pd.read_json(trend_data).to_dict()['12_months_median']

#     df = pd.concat({k: pd.DataFrame(v).T.drop('latest_point_in_time', axis=1, errors='ignore')
#         for k, v in d.items()}, axis=1) \
#         .sort_index()

#     df.index = pd.to_datetime(df.index)

#     # --- plot
#     # idx = pd.IndexSlice
#     # df.loc[:, idx[:, 'price']].plot(marker='.', legend=False)
#     # df.loc[:, idx[:, 'count']].plot(marker='.', legend=False)

#     df = pd.concat([
#             pd.DataFrame({'date': df.index.strftime('%Y-%m-%d'), 
#                         'suburb': suburb}),
#             df.reset_index(drop=True)
#         ], axis=1)

#     df.columns = ['_'.join(x) if len(x) == 2 else x for x in df.columns]

#     return df
url_base = r'https://www.realestate.com.au/neighbourhoods/'
# https://www.realestate.com.au/neighbourhoods/north-epping-2121-nsw

postcodes = pd.read_csv('postcodes-suburbs-regions.csv')
regions = ['Central & Northern Sydney', 'Southern & South Western Sydney', 'Western Sydney & Blue Mountains']

postcodes = postcodes.query('Region == @regions').reset_index(drop=True)

urls = [f'{url_base}{s.lower().replace(" ", "-")}-{p}-nsw'
        for p, s in zip(postcodes['Postcode'], postcodes['Suburb'])]

broken = []

driver = uc.Chrome()

# for url in urls:
#     driver = get_suburb_driver(url)

# debugging
driver = get_suburb_driver(urls[12])
d = get_suburb_payload(driver)

# %%%
soup = BeautifulSoup(driver.page_source, "html.parser")

payload = [s.contents[0] for
        s in soup.findAll('script')
        if len(s.contents) == 1
        and 'window.ArgonautExchange' in s.contents[0]][0]

# driver.find_element(By.XPATH, "/html/body/script")
# wait = WebDriverWait(driver, timeout=6, poll_frequency=0.1)
# wait.until(EC.presence_of_element_located())

fluent_wait(driver, condition='locate', mark=(By.XPATH, "/html/body/script"))


# %%%

# # %% scrape prices: house/unit buy/rent
# NOTE: this can be done by parsing json payload

# buy_elements = {
#     'available': 'available in the past month',
#     'sold': 'in the past 12 months',
#     'time_on_market': 'median time on market',
#     'interested': 'interested',
#     'yield': 'rental yield',
# }

# rent_elements = {
#     'available': 'available in the past month',
#     'leased': 'in the past 12 months',
#     'time_on_market': 'median time on market',
#     'interested': 'interested',
# }

# # # --- buy - house
# xpath_str = ".//div[@id='house-price-guide-buy']"
# element = fluent_wait(driver, By.XPATH, xpath_str)

# # element_tag = 'span'
# # for k, v in buy_elements.items():
# #     print(k, find_sibling_by_text(element, v, element_tag, element_tag).text)

# # --- 5 yr median prices house

# # --- rent - house

# # --- buy - apartment
# xpath_str = ".//div[@id='unit-price-guide-buy']"
# element = fluent_wait(driver, By.XPATH, xpath_str)

# # element_tag = 'span'
# # for k, v in buy_elements.items():
# #     print(k, find_sibling_by_text(element, v, element_tag, element_tag).text)

# # --- rent - apartment



# %% --- 5 yr median prices apartment

''' payload keys:
>>> payload
    ["resi-property_market-explorer"]
        ["suburb_data"]
            ["marketProfileBySlug"]
                ["insights"].keys()

<measure>: <description>
    {<temporal_key>: <val_key(s)>}
----------------------------------
'medianPrice': yearly: latest summary data (median over past 12mths)
               trends: chart data (median price and volume over past 12 mths)
    {'yearly': ['display', 'volume']  # NOTE: redundant: equal to last trend element
     'trends': ['value', 'volume'] }  # list of dicts
'transactionVolume': number sold in the past 12 months
    {'yearly': 'value'}

    "buy": {
      "house": {
        "allBed": {
          "yearly": {
            "value": 10

'daysOnSite': median time on market
    {'yearly': 'value'}

    "buy": {
      "house": {
        "allBed": {
          "yearly": {
            "value": 47

'rentalYield': rental yield (only applies to "Buy" toggle)
    {'yearly': 'display'}

    "house": {
      "allBed": {
        "yearly": {
          "display": "2.7%"


'supplyDemand': supply: properties available in the past month
                demand: interested buyers in the past 12 months
    {'monthly': ['supply', 'demand']}  # NOTE: 2 value keys

    "buy": {
      "house": {
        "allBed": {
          "monthly": {
            "supply": 5,
            "demand": 688

'''

measures = {
    'medianPrice': {
        'temporal_key': 'trends',
        'val_key': ''
    },
    'transactionVolume': {
        'temporal_key': 'yearly',
        'val_key': 'value'
    },
    'daysOnSite': {
        'temporal_key': 'yearly',
        'val_key': 'value'
    },
    'rentalYield': {
        'temporal_key': 'yearly',
        'val_key': 'display'
    },
    'supplyDemand': {
        'temporal_key': 'monthly',
        'val_key': ['supply', 'demand']
    },
}


# %% parsing payload

def parse_payload_for_measure(measure, ownership, dwelling, **m_keys):
    '''
    Extracts specific data from the json payload. Returns it in a long df.


    The json payload has [____]. This function collapses those temporal
    and value keys


    meausure: Type of data to pull. One of: [medianPrice,
        transactionVolume, daysOnSite, rentalYield, supplyDemand]
    ownership: ownership type. One of [buy, rent]
    dwelling: dwelling type. One of [house, unit]

    m_keys: kwargs for measure keys
        temporal_key:
        val_key:
    '''
    temporal_key = m_keys['temporal_key']
    val_key = m_keys['val_key']

    output_cols = ['ownership_type', 'dwelling_type', 'n_beds', 'value']

    if type(val_key) is str:
        # transactionVolume, daysOnSite and rentalYield

        output = {}

        # init dict keys as dicts
        output[ownership] = output.get(ownership, {})
        output[ownership][dwelling] = output[ownership].get(dwelling, {})

        if measure == 'rentalYield':
            d_filtered = d[measure][dwelling]
        else:
            d_filtered = d[measure][ownership][dwelling]

        output[ownership][dwelling] = {
            k: (None if n_beds[temporal_key] is None
                else n_beds[temporal_key][val_key])
                for k, n_beds in d_filtered.items()
            }
        return pd.DataFrame(
            [[ownership, dwelling, n_beds, val]
            for ownership, v in d[measure].items()
            for dwelling, vv in v.items()
            for n_beds, vvv in vv.items()
            for _, vvvv in vvv.items()
            for _, val in vvvv.items()],
            columns=output_cols)

        # process dict to longform df
        output = pd.DataFrame(
            [[_ownership, _dwelling, n_beds, val]
            for _ownership, d in output.items()
            for _dwelling, dd in d.items()
            for n_beds, val in dd.items()],
            columns=output_cols)

        output['measure'] = measure

    elif measure == 'supplyDemand':
        d_filtered = d[measure][ownership][dwelling]

        output = pd.DataFrame(
            [[ownership, dwelling, n_beds, val, meas]
             for n_beds, v in d_filtered.items()
             for _, vv in v.items()
             for meas, val in vv.items()],
            columns=[*output_cols, 'measure'])

        return output

    elif measure == 'medianPrice':
        return
    else:
        raise ValueError('Unexpected measure')

    output['queried'] = datetime.today()

    return output


output = []
for measure, m_keys in measures.items():
    # if measure != 'transactionVolume':
    if measure != 'daysOnSite':
    # if measure != 'rentalYield':
    # if measure != 'medianPrice':
    # if measure != 'supplyDemand':
         continue  # debugging
 
    for ownership, dwelling in itertools.product(['buy', 'rent'], ['house', 'unit']):
        if (measure == 'rentalYield') and (ownership == 'rent'):
            continue  # yield only available when "buy" is toggled
        temp = parse_payload_for_measure(measure, ownership, dwelling, **m_keys)
        # output += [temp]

    break

    # temp['suburb'] = get_suburb_from_url(urls[12])
temp
# pd.concat(output, axis=0, ignore_index=True)

# %% -- testing json flattening

temp = d['daysOnSite']


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
                'threeBed': {'yearly': {'value': 225}},
                'fourBed': {'yearly': None}},
            'rent': {'house': {'allBed': {'yearly': {'value': 21}},
                'twoBed': {'yearly': {'value': 20}},
                'threeBed': {'yearly': {'value': 26}},
                'fourBed': {'yearly': {'value': 33}}}
        }

    Out: [['buy', 'house', 'allBed', 'yearly', 'value', 47],
        ['buy', 'house', 'twoBed', 'yearly', 'value', 44],
        ['buy', 'house', 'threeBed', 'yearly', 'value', 225],
        ['buy', 'house', 'fourBed', 'yearly', None],
        ['rent', 'house', 'allBed', 'yearly', 'value', 21],
        ['rent', 'house', 'twoBed', 'yearly', 'value', 20],
        ['rent', 'house', 'threeBed', 'yearly', 'value', 26],
        ['rent', 'house', 'fourBed', 'yearly', 'value', 33]
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

flattened = flatten_json(temp)
# print(pd.DataFrame(flattened))

flattened


# %%
# time.sleep(1)

# buy_elements = driver.find_elements_by_xpath("//div[@class='median-price-subsection buy-subsection']")
# rent_elements = driver.find_elements_by_xpath("//div[@class='median-price-subsection rent-subsection']")

# try:
#     dummy['house_buy'] = scrape_element(buy_elements[0])
#     dummy['house_rent'] = scrape_element(rent_elements[0])
# except ValueError:
#     buy_elements = driver.find_elements_by_xpath("//div[@class='median-price-subsection buy-subsection']")
#     rent_elements = driver.find_elements_by_xpath("//div[@class='median-price-subsection rent-subsection']")
#     dummy['house_buy'] = scrape_element(buy_elements[0])
#     dummy['house_rent'] = scrape_element(rent_elements[0])
# finally:
#     broken += [(url.split(r'/')[-1], 'house error')]


# # click units to get visible text (may not be necessary with right xpath?)
# button = driver.find_element_by_xpath("//span[@class='switch-type h5 units']")
# button = WebDriverWait(driver, 10).until(lambda x: button)  # .until() takes a function, not an element
# driver.execute_script('arguments[0].scrollIntoView({block: "center"});', button)
# button.click()

# try:
#     dummy['unit_buy'] = scrape_element(buy_elements[1])
#     dummy['unit_rent'] = scrape_element(rent_elements[1])
# except (ValueError, NoSuchElementException):
#     time.sleep(1)
#     rent_elements = driver.find_elements_by_xpath("//div[@class='median-price-subsection rent-subsection']")
#     dummy['unit_buy'] = scrape_element(buy_elements[1])
#     dummy['unit_rent'] = scrape_element(rent_elements[1])
# finally:
#     broken += [(url.split(r'/')[-1], 'rent error')]


# pd.DataFrame.from_dict(dummy)  # .to_csv(f'current_prices/{suburb}.csv')

#     # %% scrape trend data
#     # click "trend" button
#     try:
#         button = driver.find_element_by_xpath("//span[@class='switch-type trend']")
#     except NoSuchElementException:
#         continue

#     button = WebDriverWait(driver, 10).until(lambda x: button)  # .until() takes a function, not an element
#     driver.execute_script('arguments[0].scrollIntoView({block: "center"});', button)

#     button.click()

#     df = scrape_trend_data(driver)

#     # %% save data
#     con = sqlite3.connect('historicalprices.db')

#     # cur = con.cursor()

#     # Create table
#     # cur.execute('''CREATE TABLE IF NOT EXISTS prices_counts (
#     #                 date text,
#     #                 suburb text,
#     #                 house_price integer,
#     #                 house_count integer, 
#     #                 unit_price integer, 
#     #                 unit_count integer
#     #                 )''')

#     # get column names from db table
#     # cur.execute('PRAGMA table_info(prices_counts);')
#     # df.columns = [x[1] for x in cur.fetchall()]

#     df.to_sql(name='prices_counts', con=con, if_exists='append', index=False)

#     # Save and close
#     con.commit()
#     con.close()
