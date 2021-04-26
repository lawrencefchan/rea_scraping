# %%
from bs4 import BeautifulSoup
import requests 
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re


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
for url in [i for i in urls if 'epping' in i]:

    driver.get(url)
    # html = driver.page_source
    # soup = BeautifulSoup(html, 'html.parser') 
    # print(soup.prettify())

    break

# %% houses
e = driver.find_element_by_xpath("//div[@class='median-price-subsection buy-subsection']")

# median
price = e.find_element_by_xpath("//div[@class='price h1 strong']").text
price = int(re.sub('[$,]', '', price))

# 2br/3br/4br
brs = ['left', 'middle', 'right']
for i in brs:
    price = e.find_element_by_xpath(f"//a[@class='breakdown-subsection {i}-subsection']" 
                                    f"//div[@class='price strong']").text
    price = int(re.sub('[$, PW]', '', price))

date = e.find_element_by_xpath(f"//div[@class='processed-date p-small']"
                        f"//span[@class='strong']").text
pd.to_datetime(date).strftime('%Y-%m-%d')

# %% rent

e = driver.find_elements_by_xpath("//div[@class='median-price-subsection rent-subsection']")

# # median
price = e[0].find_element_by_xpath(".//div[@class='price h1 strong']").text
# price = int(re.sub('[$, PW]', '', price))

price


# %% click "units" button
from selenium.webdriver.support import expected_conditions as EC

button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[@class='switch-type h5 units']"))
)
button.click()


# %% click "trend" button

button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[@class='switch-type trend']"))
)
button.click()


