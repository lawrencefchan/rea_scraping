'''
Scrapes data from www.allhomes.com.au/ah/research/property-and-past-sales
Uses suburb list to scrape suburbs -> streets -> properties

'''

# %%
import json

import pandas as pd
import requests
from bs4 import BeautifulSoup

from collections import namedtuple


def check_results(suburb):
    with open(f'{suburb}.json') as f:
        d = json.load(f)
    return d


def write_log(msg):
    with open('log.txt', 'a') as f:
        f.write(f'{pd.Timestamp.now()} {msg}\n')


def get_street_urls(row):
    '''
    row: a row from allhomes_suburb_list.csv as returned by df.itertuples().
    Contains attributes:
        - Locality
        - Suburb
    '''

    query_str = f'?localityId={row.Locality}&localityType=divisionIds&'
    query_str += f'legalSs=&ss={row.Suburb.replace(" ", "+")}'

    # Suburb landing page (contains first 50 streets)
    content = requests.get(f'{url_base}{query_str}').content
    soup = BeautifulSoup(content, 'html.parser')

    # link to Suburb Information page (contains all streets)
    url = soup.find(text='Suburbs and Towns') \
              .find_parent('div', attrs={'class': 'column'}) \
              .find(href=True)['href']
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')

    urls = soup.find(text='Streets in') \
               .find_parent('div', attrs={'class': 'column'}) \
               .find_all(href=True)

    Street = namedtuple('Street', ['name', 'url'])
    streets = [Street(i.text, i['href']) for i in urls]

    return streets


def get_property_urls(results, row, street):
    '''
    Parameters
    ----------
    **results:** a dict of results

    **row:** a row from allhomes_suburb_list.csv as returned by df.itertuples.
    Contains Locality and Suburb attributes

    **street:** namedtuple with name and url attributes

    ```
    <div class="column header">         <-- "Properties in" header
        ...
        <span class="min-format-tab-header"> <-- "Properties in" text
    <div class="linebreak"></div>       <-- linebreak
    <div class="four_column_wrapper">   <-- properties
    ```

    '''

    if results[row.Suburb].get(s, {}).get('complete') is True:
        raise StopIteration()  # already parsed
    else:
        print(row.Suburb, '-', s)
        if results[row.Suburb].get(s) is None:
            results[row.Suburb][s] = {'complete': False}

    content = requests.get(s_url).content
    soup = BeautifulSoup(content, 'html.parser')

    urls = soup.find(text='Properties in')
    if urls is None:
        results[row.Suburb][s]['complete'] = True
        raise StopIteration()

    urls = urls.find_parent('div', attrs={'class': 'column header'}) \
        .find_next_sibling('div', attrs={'class': 'four_column_wrapper'}) \
        .find_all(href=True)

    properties = [(i.text, i['href']) for i in urls]

    return properties


# list of suburbs
df = pd.read_csv('allhomes_suburb_list.csv')
df.head()

check_str = "We couldn't find any history for this property."
url_base = 'https://www.allhomes.com.au/ah/research/property-and-past-sales'

for row in df.itertuples():  # List of streets in suburb
    try:  # checks if results is defined so script can pick up where it broke
        results
        if row.Suburb not in results.keys():
            continue  # skip to the suburb being parsed when script broke
    except NameError:
        try:
            results = check_results(row.Suburb)
        except FileNotFoundError:
            results = {}

    if results.get(row.Suburb, {}).get('complete') is True:
        continue  # already parsed
    else:
        print(row.Postcode, row.Suburb)
        if results.get(row.Suburb) is None:
            results[row.Suburb] = {'complete': False}

    streets = get_street_urls(row)

    for street in streets:  # List of properties in street

        s = street.name
        s_url = street.url
        
        try:
            properties = get_property_urls(results, row, street)
        except StopIteration:
            continue

        for p, p_url in properties:  # individual property history data

            print(p)
            break
        break
    break
print('sad')

# %%
            if results[row.Suburb][s].get(p, False) is not False:
                continue  # already parsed
            # print('--', p)
            content = requests.get(p_url).content
            soup = BeautifulSoup(content, 'html.parser')

            # --- checks
            try:
                div = soup.find(attrs={'class': 'css-13it8mc'})
                assert div is not None
                assert div.text == 'Sold'
                assert soup.find(text=check_str) is None  # no error message
            except AssertionError as e:
                write_log(f'{row.Suburb}, {p}, {p_url}, {e}')
                results[row.Suburb][s][p] = None
                continue

            # else: property history exists
            history_div = soup.find_all(attrs={'class': 'css-1waaw1k'})

            # scrape sales history
            data = []
            for div in history_div:
                d = [i.text for
                     i in div.find_all(attrs={'class': 'css-104pj7g'})]
                d = dict(i.split(': ') for i in d)
                d['Price'] = div.find(attrs={'class': 'css-wtlu8o'}).text

                data += [d]

            # scrape dwelling specs.
            specs = {}
            spec_div = soup.find(attrs={'class': 'css-1qq148s etrbpx50'})

            if spec_div is not None:
                div = spec_div.find(attrs={'class': 'css-1apbjvj etrbpx51'})

                if div is not None:  # specs available
                    specs['type'] = div.text

                    room_div = spec_div.find_all(attrs={
                        'class': 'css-8dprsf etrbpx52'})
                    for room in room_div:
                        specs[room.find('title').text] = room.find(attrs={
                            'class': 'css-17k95w5 etrbpx53'}).text

            # --- checks
            try:
                assert len(data) > 0
            except AssertionError as e:
                write_log(f'{row.Suburb}, {p}, {p_url}, {e}')
                results[row.Suburb][s][p] = None
                continue

            results[row.Suburb][s][p] = {}
            results[row.Suburb][s][p]['transfers'] = data
            results[row.Suburb][s][p].update(specs)
            # break  # break after completing one property

        results[row.Suburb][s]['complete'] = True
        # break  # break after completing one street

    results[row.Suburb]['complete'] = True
    # break  # break after completing one suburb

    # save and clear results after completing each suburb
    with open(f'{row.Suburb}.json', 'w') as f:
        json.dump(results, f)

    results = {}

print('complete')


# %% save results
with open('results.json', 'w') as f:
    json.dump(results, f)

# load results
# with open('results.json') as f:
#     results = json.load(f)


