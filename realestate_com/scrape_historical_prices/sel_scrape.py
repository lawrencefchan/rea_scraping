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
import json
import pandas as pd
from datetime import datetime

from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup  
import undetected_chromedriver as uc  # anti-bot selenium patch

from utils.sqlite_utils import write_snapshot_to_db
from utils.selenium_utils import (
    fluent_wait,
    find_sibling_by_text
)


URL_ROOT = r'https://www.realestate.com.au/neighbourhoods/'


def sectors():
    '''
    returns o, d
    '''
    ownership_type = ('buy', 'rent')
    dwelling_type = ('house', 'unit')
    return ((o, d) for o in ownership_type for d in dwelling_type)


def get_sydney_suburbs_urls():
    '''
    Returns [(suburb, suburb_url), ...] for each suburb in the postcode list.
    '''
    regions = [
        'Central & Northern Sydney',
        'Southern & South Western Sydney',
        'Western Sydney & Blue Mountains']

    postcodes = pd.read_csv('postcodes-suburbs-regions.csv')
    postcodes = postcodes.query('Region == @regions').reset_index(drop=True)

    urls = [(s.lower().replace(" ", "-"), f'{URL_ROOT}{s.lower().replace(" ", "-")}-{p}-nsw')
            for p, s in zip(postcodes['Postcode'], postcodes['Suburb'])]

    return urls

# todo:
# implement a way to find url from suburb name

def get_suburb_from_url(url):
    '''
    Returns the suburb name given by a realestate.com neighbourhood url.
    '''
    return (' ').join(url.split(r'/')[-1].split('-')[:-2])


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

def flatten_json(d, keys=[], flattened_output=[]):
    '''
    Takes a json and returns it as a list so it can be converted to
    table format and written into a database.

    Usage: (BUG)
    ------
    Function MUST be called like `flatten_json(input_df, [], [])` to work.
    For some reason the output variable is retained across function calls,
    so successive calls will compound outputs.

    Parameters:
    -----------
    d: the dictionary to flatten
    keys: unused arg to pass down recursive variables
    flattened_output: unused arg to pass down recursive variables

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
            flatten_json(v, new_keys, flattened_output)
        else:
            # print([*new_keys, v])
            flattened_output += [[*new_keys, v]]
            new_keys = new_keys[:-1]

    return flattened_output


def get_measures_from_dict(payload):
    '''
    
    NOTE:
    * medianPrice, transactionVolume processed separately
    * for n_beds, 0 is aggregate median of all other n_beds
    '''

    measures = {  # <measure>: [levels to drop]
        'daysOnSite': [3, 4],
        'rentalYield': [2, 3],
        'supplyDemand': [3],
    }

    output = []
    cols = ['ownership_type', 'dwelling_type', 'n_beds']

    for m, v in measures.items():
        df = pd.DataFrame(flatten_json(payload[m], [], [])) \
                .drop(v, axis=1)

        if m == 'supplyDemand':
            df.columns = [*cols, '.', '..']
            df = df.pivot_table(index=cols, columns='.', values='..')
        else:
            if m == 'rentalYield':
                df.insert(loc=0, column='_', value='buy')
                df[4] = df[4].str[:-1].astype(float)

            df.columns = [*cols, m]
            df = df.set_index(cols)

        output += [df]

    # final processing
    output = pd.concat(output, axis=1).reset_index()
    output['last_queried'] = datetime.today().date()
    output['n_beds'] = output['n_beds'].replace({
        'allBed': 0,
        'oneBed': 1,
        'twoBed': 2,
        'threeBed': 3,
        'fourBed': 4,
        'fiveBed': 5,
        })

    try:
        assert not output['n_beds'].isnull().any()
    except AssertionError:
        raise ValueError('Not all bedroom types have been mapped.')

    return output.sort_values(cols)


# driver = uc.Chrome()

# urls = get_sydney_suburbs_urls()
# # broken = []
# # for suburb, url in urls:
# #     d = scrape_suburb_data(url)

# # --- debugging
# suburb, url = urls[12]
# payload = scrape_suburb_data(url)
df = get_measures_from_dict(payload)
df.insert(loc=0, column='suburb', value=suburb)

write_snapshot_to_db(df)

# %%
# --- trends
# get beds
for ownership_type, dwelling_type in sectors():
    temp_d = payload['medianPrice'][ownership_type][dwelling_type]
    for k in temp_d.keys():
        trends = temp_d[k]['trends']
        if trends is not None: print(ownership_type, dwelling_type, k, len(trends))

# %%

df_trends = pd.DataFrame(trends) \
        .drop(['display', 'startDate'], axis=1) \
        .rename(columns={'endDate': 'yr_ended', 'value': 'median'})

df_trends['ownership_type'] = ownership_type
df_trends['dwelling_type'] = dwelling_type
df_trends['n_beds'] = k

# %%
df_trends[df_trends['yr_ended'] == df_trends['yr_ended'].max()]
