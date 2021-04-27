# %%
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url_base = r'https://www.realestate.com.au/neighbourhoods/'
postcodes = pd.read_csv('suburb_postcodes.csv')
# https://www.realestate.com.au/neighbourhoods/north-epping-2121-nsw

options = webdriver.ChromeOptions()
options.add_argument("disable-blink-features=AutomationControlled")
options.add_argument("--incognito")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(executable_path="chromedriver90.exe", options=options)

# %%
urls = [f'{url_base}{s.lower().replace(" ", "-")}-{p}-nsw'
        for p, s in zip(postcodes['Postcode'], postcodes['Suburb'])]

for url in [i for i in urls if 'epping' in i]:
    suburb = url.split(r'/')[-1]
    driver.get(url)

    # html = driver.page_source
    # soup = BeautifulSoup(html, 'html.parser') 
    # print(soup.prettify())

    break
# %% various dicts

# 2br/3br/4br
brs = {
    'median_2br': 'left',
    'median_3br': 'middle',
    'median_4br': 'right'
}

data = {}

dummy = {
    'house_buy': {
        'median': 'price',
        'median_2br': 'median_2br',
        'median_3br': 'median_3br',
        'median_4br': 'median_4br',
        'updated': 'date'
    },
    'house_rent': {
        'median': 'price',
        'median_2br': 'median_2br',
        'median_3br': 'median_3br',
        'median_4br': 'median_4br',
        'updated': 'date'
    },
    'unit_buy': {
        'median': 'price',
        'median_2br': 'median_2br',
        'median_3br': 'median_3br',
        'median_4br': 'median_4br',
        'updated': 'date'
    },
    'unit_rent': {
        'median': 'price',
        'median_2br': 'median_2br',
        'median_3br': 'median_3br',
        'median_4br': 'median_4br',
        'updated': 'date'
    }
}

data['dummy'] = dummy


# %%
def scrape_element(element):
    '''Returns a dict of all data for a given web element (price subsection)'''

    d = {
        'median': '',
        'median_2br': '',
        'median_3br': '',
        'median_4br': '',
        'updated': ''
    }

    price = element.find_element_by_xpath(".//div[@class='price h1 strong']").text
    price = int(re.sub('[$, PW]', '', price))
    d['median'] = price

    # 2br/3br/4br
    for k, v in brs.items():
        price = element.find_element_by_xpath(f".//a[@class='breakdown-subsection {v}-subsection']" 
                                        f"//div[@class='price strong']").text
        price = int(re.sub('[$, PW]', '', price))
        d[k] = price

    date = element.find_element_by_xpath(f".//div[@class='processed-date p-small']"
                            f"//span[@class='strong']").text
    d['updated'] = pd.to_datetime(date).strftime('%Y-%m-%d')

    return d

# %% scrape prices: house/unit buy/rent
buy_elements = driver.find_elements_by_xpath("//div[@class='median-price-subsection buy-subsection']")
rent_elements = driver.find_elements_by_xpath("//div[@class='median-price-subsection rent-subsection']")

dummy['house_buy'] = scrape_element(buy_elements[0])
dummy['house_rent'] = scrape_element(rent_elements[0])

# click units to get visible text (may not be necessary with right xpath?)
button = driver.find_element_by_xpath("//span[@class='switch-type h5 units']")
button = WebDriverWait(driver, 10).until(lambda x: button)  # .until() takes a function, not an element
driver.execute_script('arguments[0].scrollIntoView({block: "center"});', button)
button.click()

dummy['unit_buy'] = scrape_element(buy_elements[1])
dummy['unit_rent'] = scrape_element(rent_elements[1])


dummy


# %% click "trend" button
button = driver.find_element_by_xpath("//span[@class='switch-type trend']")
button = WebDriverWait(driver, 10).until(lambda x: button)  # .until() takes a function, not an element
driver.execute_script('arguments[0].scrollIntoView({block: "center"});', button)

button.click()

# %% trend data
trend_element = driver.find_element_by_xpath("//div[@class='slide-section median-price-subsections trend']")
trend_data = trend_element.get_attribute('data-trend')

# %%
d = pd.read_json(trend_data).to_dict()['12_months_median']

df = pd.concat({k: pd.DataFrame(v).T.drop('latest_point_in_time', axis=1, errors='ignore')
    for k, v in d.items()}, axis=1) \
    .sort_index()

df.index = pd.to_datetime(df.index)

idx = pd.IndexSlice
df.loc[:, idx[:, 'price']].plot(marker='.', legend=False)
df.loc[:, idx[:, 'count']].plot(marker='.', legend=False)

# %%

