import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from config import (
    NAME,
    BASE_URL,
    DIRECTORY,
    DIR_LOG
)
from selenium.common.exceptions import NoSuchElementException,ElementNotVisibleException, ElementNotSelectableException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import pandas as pd
from datetime import datetime
from random import randint
import undetected_chromedriver as uc
from loguru import logger
from random import randint
import numpy as np
from nordvpn_switcher import initialize_VPN,rotate_VPN,terminate_VPN
import sys
import csv
from pathlib import Path

#Logger information
#logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add("log_file_{time}.log")


def set_options():
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    prefs = {"profile.managed_default_content_settings.images": 2,
             "disk-cache-size": 4096}
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--ignore-certificate-error")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--headless")
    #chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #chrome_options.add_experimental_option('useAutomationExtension', False)
    #chrome_options.add_argument("no-default-browser-check")
    #chrome_options.add_argument("disable-dev-shm-usage")
    #chrome_options.add_argument('log-level=3')
    return chrome_options
    
def detect_verification(driver):
    wait = WebDriverWait(driver, timeout=45,poll_frequency=1, ignored_exceptions=[TimeoutException])
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="captcha_submit"]'))).click()
    except:
        logger.debug('Human verification not present')

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

def get_element(driver):
    wait = WebDriverWait(driver, timeout=45, poll_frequency=1, ignored_exceptions=[TimeoutException])
    return wait.until(EC.presence_of_all_elements_located((By.XPATH,"//td[@class='row_name']//a")))
     
def get_rand_int():
    return randint(1, 8146)

def _run():
    
    
    
    pass


def main():
    initialize_VPN(stored_settings=1)
    #IMPLEMENT NORD VPN SWITCHER TO BYPASS ISSUES, AFTER 20 PAGES
    #URL page1
    BASE_URL = "https://myip.ms/browse/sites/1/ownerID/376714/ownerID_A/1"
    rotate_VPN()
    #List to store all the links
    url_dict = {}
    #pdf to store the table containing the links
    df_urls = pd.DataFrame()
    #IMPLEMENT RANDOM NUMBER GENERATOR TO SCRAPE IPS FROM RANDOM PAGES, UP TO 9000
    #Create a set (cointainer with no duplicated values) to store the random integer number generated > the list will store the numbers > not to be re-used
    with open('list_randomPages_pulled.txt') as file:
        rnd_list = file.read().split(' ')
    #Make 10 dynamic
    n = 0
    #list of columns containing the rnd link being pulled out
    columns = []
    df_ = pd.DataFrame()
    with pd.ExcelWriter(Path.cwd() / 'test_excel_new.xlsx', engine="openpyxl") as xfile:
        for _ in range(45):
            logger.debug(f"the count is: {n}")
            #The link will be randomly generated
            rnd_link = get_rand_int()
            while True:
                if rnd_link in rnd_list:
                    rnd_link = get_rand_int()
                else:
                    logger.debug("New random number added to list")
                    rnd_list.append(str(rnd_link))
                    with open('list_random_pages.txt', 'a') as file:
                        file.write(';'+str(rnd_link)) 
                    break
            logger.info(f"The random list of generated number is: {rnd_list}")
            link = f'/{rnd_link}/'
            if link ==  '1':
                page_url = BASE_URL
            else:
                page_url = get_url(link,BASE_URL)
            logger.info("Driver and Wait defined")
            #Define the options
            try:
                #Create a function to standardize opening URL and GET element actions
                options = set_options()
                #Define the driver
                driver = webdriver.Chrome(options=options)
                logger.info(f"Opening the URL page: {page_url}")
                driver.get(page_url)
                detect_verification(driver)
                logger.debug(driver.current_url)
                wait = WebDriverWait(driver, timeout=30, ignored_exceptions=[TimeoutException])
                wait.until(EC.visibility_of_element_located((By.XPATH, "//strong[contains(text(),'World Web Sites Hosting Information Directory (Dec')]")))
                result_list = get_element(driver)
                logger.debug(result_list)
                #logger.debug(result_list)
                links = ["https:" + result_list[i].text for i in range(len(result_list))]    
                logger.debug(f"The links are: {links}")
            except:
                logger.debug("Cannot get the links")
            url_dict[rnd_link] = links
            df_urls[rnd_link] = links
            if n == 15:
                #Switch VPN to a different IP
                logger.debug("Switch IP address")
                rotate_VPN()
                n=0
            n+= 1
            driver.quit()
        df_urls.to_excel(xfile, sheet_name='sheet1')
        #xfile.save()
    return df_urls  
            
if __name__ == '__main__':
    time_to_append = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = "table_urls_" + time_to_append + '.xlsx'
    cwd = Path.cwd() #setting current working directory
    output =  main() 
    with pd.ExcelWriter(cwd / filename) as writer:
        output.to_excel(writer, sheet_name='sheet1')
