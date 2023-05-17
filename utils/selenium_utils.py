'''
Xpath notes:
* the period in ".//" searches within the given element, rather than searching
the entire document from the root, like "//" would.
'''

from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import (
    ElementNotVisibleException,
    ElementNotSelectableException
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def fluent_wait(driver, mark, condition='click'):
    '''
    condition: 
    mark: same args as find_element, e.g. (By.XPATH, ".//p[@data='clearance-']")
    '''
    if condition == 'click':
        cond = EC.element_to_be_clickable
    elif condition == 'locate':
        cond = EC.presence_of_element_located

    ignore = [ElementNotVisibleException, ElementNotSelectableException]
    wait = WebDriverWait(driver, timeout=6, poll_frequency=0.1, ignored_exceptions=ignore)
    element = wait.until(cond((mark)))

    return element


def find_sibling_by_text(driver, text: str,
                         target_tag=None, sibling_tag=None, sibling_position=None):
    '''
    Searches elements that contain a target string and returns text of
    the preceding sibling.
    '''

    if sibling_tag is None:
        sibling_tag = '*'
    if target_tag is None:
        target_tag = '*'
    if sibling_position is None:
        sibling_position = 'preceding'

    target_xpath = f".//{target_tag}[contains(text(), '{text}')]"
    sibling_xpath = f"/{sibling_position}-sibling::{sibling_tag}[1]"  # [1] gets the immediate closest sibling

    element = fluent_wait(driver, mark=(By.XPATH, target_xpath+sibling_xpath))

    return element