# %%
from bs4 import BeautifulSoup
import pandas as pd
import re

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
data


# %% houses - buy/rent
buy_elements = driver.find_elements_by_xpath("//div[@class='median-price-subsection buy-subsection']")

# --- buy
price = buy_elements[0].find_element_by_xpath(".//div[@class='price h1 strong']").text
price = int(re.sub('[$,]', '', price))
dummy['house_buy']['median'] = price

# 2br/3br/4br
for k, v in brs.items():
    price = buy_elements[0].find_element_by_xpath(f".//a[@class='breakdown-subsection {v}-subsection']" 
                                    f"//div[@class='price strong']").text
    price = int(re.sub('[$, PW]', '', price))
    dummy['house_buy'][k] = price

date = buy_elements[0].find_element_by_xpath(f".//div[@class='processed-date p-small']"
                        f"//span[@class='strong']").text
dummy['house_buy']['updated'] = pd.to_datetime(date).strftime('%Y-%m-%d')

# --- rent
rent_elements = driver.find_elements_by_xpath("//div[@class='median-price-subsection rent-subsection']")

price = rent_elements[0].find_element_by_xpath(".//div[@class='price h1 strong']").text
price = int(re.sub('[$, PW]', '', price))
dummy['house_rent']['median'] = price

# 2br/3br/4br
for k, v in brs.items():
    price = rent_elements[0].find_element_by_xpath(f".//a[@class='breakdown-subsection {v}-subsection']" 
                                    f"//div[@class='price strong']").text
    price = int(re.sub('[$, PW]', '', price))
    dummy['house_rent'][k] = price

date = rent_elements[0].find_element_by_xpath(f".//div[@class='processed-date p-small']"
                        f"//span[@class='strong']").text
dummy['house_rent']['updated'] = pd.to_datetime(date).strftime('%Y-%m-%d')

dummy

# %% click "units" button

# button = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, "//span[@class='switch-type h5 units']"))
# )
button = e.find_element_by_xpath(
    "//span[@class='switch-type h5 units']")
button = WebDriverWait(driver, 10).until(lambda x: button)  # .until takes a function, not an element
driver.execute_script('arguments[0].scrollIntoView({block: "center"});', button)

button.click()

# %% unit - buy/rent

# buy
price = buy_elements[1].find_element_by_xpath(".//div[@class='price h1 strong']").text
price = int(re.sub('[$,]', '', price))
dummy['unit_buy']['median'] = price

for k, v in brs.items():
    price = buy_elements[1].find_element_by_xpath(f".//a[@class='breakdown-subsection {v}-subsection']" 
                                    f"//div[@class='price strong']").text
    price = int(re.sub('[$, PW]', '', price))
    dummy['unit_buy'][k] = price

date = buy_elements[1].find_element_by_xpath(f".//div[@class='processed-date p-small']"
                        f"//span[@class='strong']").text
dummy['unit_buy']['updated'] = pd.to_datetime(date).strftime('%Y-%m-%d')

# rent
price = rent_elements[1].find_element_by_xpath(".//div[@class='price h1 strong']").text
price = int(re.sub('[$, PW]', '', price))
dummy['unit_rent']['median'] = price

# 2br/3br/4br
for k, v in brs.items():
    price = rent_elements[1].find_element_by_xpath(f".//a[@class='breakdown-subsection {v}-subsection']" 
                                    f"//div[@class='price strong']").text
    price = int(re.sub('[$, PW]', '', price))
    dummy['unit_rent'][k] = price

date = rent_elements[1].find_element_by_xpath(f".//div[@class='processed-date p-small']"
                        f"//span[@class='strong']").text
dummy['unit_rent']['updated'] = pd.to_datetime(date).strftime('%Y-%m-%d')
dummy

# %% click "trend" button

button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[@class='switch-type trend']"))
)
button.click()


