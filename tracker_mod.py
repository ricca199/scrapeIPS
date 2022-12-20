import time
from selenium.webdriver.common.keys import Keys
from config import (
    NAME,
    BASE_URL,
    DIRECTORY,
    DIR_LOG
)
from selenium.common.exceptions import NoSuchElementException,ElementClickInterceptedException,ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import json
from datetime import datetime
from random import randint
import undetected_chromedriver as uc
from loguru import logger
import sys

#Logger information
#logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add("log_file_{time}.log")


def get_links(result_list):
        #Extract all the https from page1 and store them in a list
        links = ["https:" + result_list[i].text for i in range(len(result_list))]
        return links

def get_url(link,url):
    page_split = url.split('/1/')
    end_link = link[:1]
    new_page = page_split[0] + link + page_split[1]
    logger.debug(f'The new page is: {new_page}')
    return new_page

def get_page_element(driver,id):
    xpath = f"div[class='sites_tbl_paging'] a:nth-child({id})"
    #div[class='sites_tbl_paging'] a[class='aqPagingSel']
    #div[class='sites_tbl_paging'] a:nth-child(4)
    return driver.find_element(By.CSS_SELECTOR,xpath).click()

def get_element(driver):
    return driver.find_elements(By.XPATH, "//td[@class='row_name']//a")
 
def main():
    #URL page1
    BASE_URL = "https://myip.ms/browse/sites/1/ownerID/376714/ownerID_A/1"
    #List to store all the links
    url_list = []
    driver = uc.Chrome(version=108)
    driver.get(BASE_URL)
    result_list = get_element(driver)
    url_list.append(get_links(result_list))
    for i in range(2,10):
        logger.info(f"Pulling {i} page from IPS and refreshing the driver")
        #driver.refresh()
        link = i
        get_page_element(driver,link)
        #wait = WebDriverWait(driver, 10, 2, ignored_exceptions=[NoSuchElementException,ElementClickInterceptedException,ElementNotVisibleException])
        #w = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="captcha_submit"]')))
        #w.click()
        try:
            driver.implicitly_wait(3)
            wait = driver.find_element(By.XPATH,'//*[@id="captcha_submit"]')
            if wait.is_displayed():
                wait.click()
                driver.implicitly_wait(3)
                wait2 = driver.find_element(By.XPATH,'//*[@id="captcha_submit"]')
                if wait2.is_displayed():
                    wait2.click()
                get_page_element(driver,link)
            else:
                logger.debug("No Alert")
        except Exception as e:
            logger.debug(f"No Exception")
        result_list = get_element(driver)
        links = get_links(result_list)
        url_list.append(links)
    driver.quit()
    return url_list
            
                   
if __name__ == '__main__':
   url_list =  main()