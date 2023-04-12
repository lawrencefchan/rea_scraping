# %%
import time
import pandas as pd
import numpy as np

import undetected_chromedriver as uc  # anti-bot selenium patch
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def check_travel_time(driver, destination: str, origin: str):
    '''
    Checks door-to-door travel time using google maps. Default trip is
    monday morning at 9am.
    Note: addresses use the closest match according to google

    Returns travel time as an average of the top results.

    driver: selenium web driver
    origin: address to start from
    destination: address to end up at
    
    '''

    def str_time_to_minutes(time_str):
        '''
        Takes time in the form "x hr y min" and returns minutes as an int
        '''
        time_str = time_str.replace(' min', '')
        time_str = [int(j) for j in time_str.split('hr ')]
        if len(time_str) == 2:
            time_str = time_str[0] * 60 + time_str[1]
        else:
            time_str = time_str[0]

        return time_str

    driver.get(url)

    # find search box and enter destination address
    search_box = driver.find_element(By.XPATH, "//input[@id='searchboxinput']")
    search_box.send_keys(origin)

    # get directions to address (opens "directions from")
    driver.find_element(By.XPATH, "//button[@aria-label='Directions']").click()

    # enter work address
    time.sleep(2)  # todo: fix this - it's fragile
    actions = ActionChains(driver)
    actions.send_keys(destination + '\n')
    actions.perform()

    # reverse travel direction (i.e. travel from home to work)
    xpath_str = "//button[@aria-label='Reverse starting point and destination']"
    driver.find_element(By.XPATH, xpath_str).click()

    # set arrive by details
    driver.find_element(By.XPATH, "//div[@aria-label='Departure options']").click()
    xpath_str = f"//*[contains(text(), 'Arrive by')]"
    driver.find_element(By.XPATH, xpath_str).click()

    # arrive by 9am
    search_box = driver.find_element(By.XPATH, "//input[@name='transit-time']")
    search_box.clear()
    search_box.send_keys('9:00am')
    search_box.send_keys(Keys.RETURN)

    # arrive on monday
    # open calendar
    date_box = driver.find_element(By.XPATH, "//span[@jsaction='openDatePicker']")
    date_box.click()
    # click first col, last row (monday is first column by default)
    # todo: this will not work if the current date is after the last monday of the current calendar page
    date_button = driver.find_element(By.XPATH, "//td[@role='gridcell'][@id=':2g']")
    date_button.click()

    # set travel via public transport
    xpath_str = "//img[@data-tooltip='Public transport']"
    transport = driver.find_element(By.XPATH, xpath_str)
    transport.click()

    # get time for list of ways to get to destination
    xpath_str = "//div[@class='m6QErb']/*"  # '/*' is immediate children | class value looks fragile
    travel_options = driver.find_elements(By.XPATH, xpath_str)

    def get_travel_time_from_element(element):
        travel_time = element.get_attribute('aria-label')

        if travel_time is None:  # unusual behaviour, possibly google recommends walking?
            xpath_str = "//div[@class='Fk3sm fontHeadlineSmall']"
            travel_time = driver.find_element(By.XPATH, xpath_str).text

        travel_time = travel_time.split(', ')[-1]  # removes mode of transport, times

        return travel_time

    str_times = [get_travel_time_from_element(i) for i in travel_options]

    return np.mean([str_time_to_minutes(i) for i in str_times])


if __name__ == "__main__":

    driver = uc.Chrome()
    driver.implicitly_wait(10) # affects all following elements in the session

    url = 'https://maps.google.com'
    driver.get(url)

    # df = pd.read_csv('realestate_com\saved_properties_20230409.csv')
    df = pd.read_csv('saved_properties_20230409.csv')

    output = []
    for address in df['address'][5:6]:
        d = {}

        d['address'] = address
        d['mn'] = check_travel_time(driver, 'merewether building', address)
        d['lc'] = check_travel_time(driver, '20 bond st', address)

        output += [d]

    output = pd.DataFrame(output)
