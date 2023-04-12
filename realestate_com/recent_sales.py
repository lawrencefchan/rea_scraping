# %%

import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc  # anti-bot selenium patch
from selenium.webdriver.common.by import By

driver = uc.Chrome()

home = 'https://www.realestate.com.au/auction-results/'
states = ['nsw', 'qld', 'sa', 'wa', 'nt', 'act', 'tas']

url = home + states[0]
# url = 'https://www.domain.com.au/auction-results/sydney/'
url = 'https://www.realestate.com.au/auction-results/nsw'
driver.get(url)

# %% state profile

def get_state_profile(driver):
    '''
    Parses the 
    '''

    def find_sibling_by_text(driver, text: str):
        '''
        Searches elements that contain a given string and returns text of
        the preceding sibling.
        '''
        xpath_str = f"//*[contains(text(), '{text}')]/preceding-sibling::p[1]"
        value = driver.find_element(By.XPATH, xpath_str).text

        return int(value.replace(',', ''))

    properties = [
        'Sold at auction',
        'Sold prior to auction',
        'Sold after auction',
        'Withdrawn',
        'Passed in',
        'Private sales'
    ]

    profile = {p: find_sibling_by_text(driver, p) for p in properties}

    cr = driver.find_element(By.XPATH, "//p[@data-testid='number-pie']").text
    profile['clearance rate'] = int(cr.replace('%', '')) * 0.01

    return profile


get_state_profile(driver=driver)



# %% get suburb links (bs4 is faster)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

suburb_links = [f"https://www.realestate.com.au{l['href']}"
                for l in soup.find_all('a', href=True)
                if '/auction-results/' in l['href']][1:]

suburb_links


# %% Close the driver
driver.quit()


