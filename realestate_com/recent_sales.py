# %%

import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup

import undetected_chromedriver as uc  # anti-bot selenium patch
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    ElementNotVisibleException,
    ElementNotSelectableException
)
from selenium.webdriver.support import expected_conditions as EC


def get_state_profile(driver):
    '''
    Parses latest auction and sales results.

    Todo:
    * parse domain.com (www.domain.com.au/auction-results/sydney)

    '''

    def find_sibling_by_text(driver, text: str):
        '''
        Searches elements that contain a given string and returns text of
        the preceding sibling.
        '''

        xpath_str = f"//*[contains(text(), '{text}')]/preceding-sibling::p[1]"

        # value = driver.find_element(By.XPATH, xpath_str).text
        value = fluent_wait(driver, By.XPATH, xpath_str).text
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

    # get clearance rate
    try:  # NA when no houses are auctioned (fluent_wait will timeout)
        cr = fluent_wait(driver, By.XPATH, "//p[@data-testid='number-pie']").text
        profile['clearance rate'] = int(cr.replace('%', '')) * 0.01
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


def fluent_wait(driver, *wait_args):
    '''
    wait_args: same args as find_element, e.g. (By.XPATH, "//p[@data='clearance-']")
    '''
    ignore = [ElementNotVisibleException, ElementNotSelectableException]
    wait = WebDriverWait(driver, timeout=6, poll_frequency=0.1, ignored_exceptions=ignore)
    element = wait.until(EC.element_to_be_clickable((wait_args)))
    return element


if __name__ == "__main__":
    
    driver = uc.Chrome()
    driver.minimize_window()

    # # --- debugging
    # url = 'https://www.realestate.com.au/auction-results/wa'
    # driver.get(url)
    # d = get_state_profile(driver)

    d = profile_all_states(driver)
    df = munge_profile_output(d)


# %%


# %% get suburb links (bs4 is faster)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

suburb_links = [f"https://www.realestate.com.au{l['href']}"
                for l in soup.find_all('a', href=True)
                if '/auction-results/' in l['href']][1:]

suburb_links


# %% Close the driver
driver.quit()


