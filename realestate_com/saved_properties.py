'''
Notes:
* undetected_chromedriver is used because realestate.com.au blocks selenium
* we use bs4 because it seems to scrape page content faster

todos:
* build sqllite library
* credential manager??
* 
'''
# %%
from datetime import datetime

import pandas as pd

from bs4 import BeautifulSoup

import undetected_chromedriver as uc  # anti-bot selenium patch
from selenium.webdriver.common.by import By


def load_uc_session():
    '''
    Loads an undetected chromedriver session and logs into realestate.com.au
    '''
    driver = uc.Chrome()
    driver.implicitly_wait(10) # affects all following elements in the session

    url = 'https://www.realestate.com.au/collections/saved-properties/'
    driver.get(url)

    # -- login
    user = 'lawrence.fchan@gmail.com'
    pw = '7flRLZLc5TF5'

    user_input = driver.find_element(By.XPATH, "//input[@name='username']")
    user_input.send_keys(user)

    pw_input = driver.find_element(By.XPATH, "//input[@name='password']")
    pw_input.send_keys(pw)
    pw_input.submit()

    return driver


def get_saved_listings(driver):
    '''
    Pulls urls for all saved listings.

    Note:
        * the web version of realestate.com.au doesn't split collections, so
        all saved listings are parsed.
    '''
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    class_name = 'Card__Box-sc-g1378g-0 fNGfHf ModifiedConstruct__ListingCard-sc-1ybj4lx-2 jcskAp'
    listing_urls = [i.find('a', href=True)['href']
                    for i in soup.find_all(class_=class_name)]

    return listing_urls


def scrape_listing(driver, url):
    '''
    Scrapes details for a given realestate.com.au listing.

    Todo:
        * save pictures in a folder

    Returns a dict of details for each listing: {
        'address': '',
        'list price': '',
        'beds': '',
        'baths': '',
        'cars': '',
        'land': '',
    }

    '''
    driver.get(url)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    d = {  # these properties can be found with the basic soup.find
        'address': 'property-info-address',
        'list price': 'property-price property-info__price',
        }

    listing_details = {k: soup.find(class_=v).text for k, v in d.items()}

    # other property attributes (need to check .svg sprites)
    div = soup.find(attrs={"class": ["property-info__property-attributes"]})
    sprites = div.find_all('use', href=True)  

    for attr in ['beds', 'baths', 'cars', 'land']:
        elements = [s for s in sprites if attr in s['href']]
        if len(elements) == 0:
            listing_details[attr] = 0
            continue

        try:
            assert len(elements) == 1
        except AssertionError:
            print('unexpected number of elements in', url)

        listing_details[attr] = elements[0].parent.parent.get_text(strip=True)

    return listing_details


def munge(listing_details: list, saveas: str):
    '''
    Munges scraped listings into a nicer format.

    listing_details: list of dicts
    saveas: string to save .csv file as
    '''
    df = pd.DataFrame(listing_details)

    df['list price'] = df['list price'].str.split('$').str[1]

    cols = ['list price', 'land']
    for c in cols:
        df[c] = df[c].str.replace(',', '')

    cols = ['list price', 'beds', 'baths', 'cars']
    df[cols] = df[cols].fillna(0).astype(int)

    df['land'] = df['land'].astype(float)

    df['last updated'] = datetime.now().strftime('%Y-%m-%d')

    if saveas is not None:
        df.to_csv(saveas, index=False)
    return df


if __name__ == '__main__':
    driver = load_uc_session()
    listing_urls = get_saved_listings(driver)
        
    details = []
    for url in listing_urls:
        details += [scrape_listing(driver, url)]

    saveas = f'saved_properties_{datetime.now().strftime("%Y%m%d")}.csv'
    df = munge(details, saveas=saveas)

    driver.quit()

