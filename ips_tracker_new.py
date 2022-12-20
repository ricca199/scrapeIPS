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
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
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
from twocaptcha import TwoCaptcha
from loguru import logger
from random import randint
import numpy as np
import sys
import os
from nordvpn_switcher import initialize_VPN,rotate_VPN,terminate_VPN
import csv
from pathlib import Path

#Logger information
#logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add("log_files/log_file_{time}.log")


def set_options():
    
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    prefs = {"profile.managed_default_content_settings.images": 2,
             "disk-cache-size": 4096}
    #chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument("--ignore-certificate-error")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("no-default-browser-check")
    chrome_options.add_argument("disable-dev-shm-usage")
    chrome_options.add_argument('log-level=3')
    return chrome_options
    
def detect_verification(driver):
    api_key = os.getenv('APIKEY_2CAPTCHA', '186ae58c723e40dff69ed17b0b04b652')
    solver = TwoCaptcha(api_key)
    try:
        wait = WebDriverWait(driver, timeout=60, ignored_exceptions=[TimeoutException])
        wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="captcha_submit"]')))
        #GET the image, solve it and enter the captcha
        try:
            captcha_img = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/center/form/img")
            logger.debug(f"Captcha image detected and stored")
            captcha_img.screenshot('captchas/captcha.png')
            result = solver.normal('captchas/captcha.png')
            code = result['code']
            logger.debug(f"The result of the captch is: {code}")
            driver.find_element(By.XPATH, '//*[@id="p_captcha_response"]').send_keys(code)
        except:
            logger.debug("Captcha not present")
        #/html/body/div[2]/div/div/div/center/form/img
        #//*[@id="p_captcha_response"]
        element = driver.find_element(By.XPATH, '//*[@id="captcha_submit"]')
        logger.debug(f"Element is displayed: {element.is_displayed()}")
        element.click()
    except:
        logger.debug("No Human verification appeared")
        return     
    
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
    #wait = WebDriverWait(driver, timeout=45, poll_frequency=1, ignored_exceptions=[TimeoutException])
    #return wait.until(EC.presence_of_all_elements_located((By.XPATH,"//td[@class='row_name']//a")))
    return driver.find_elements(By.XPATH,"//td[@class='row_name']//a")

def get_rand_int():
    return randint(1, 8146)

def get_option_url():
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"
    logger.info("Options and driver are being defined")
    options = set_options()
    #Define the driver
    driver = webdriver.Chrome(options=options)
    return driver
    
def _run(driver,page_url):
    logger.info(f"Opening the URL page: {page_url}")
    driver.get(page_url)
    #driver.implicitly_wait(2)
    logger.info("Detecting Human Verification")
    detect_verification(driver)
    driver.implicitly_wait(5)
    logger.debug(driver.current_url)
    #Wait for the urls in table to be visible
    wait = WebDriverWait(driver, timeout=60, ignored_exceptions=[TimeoutException])
    element = wait.until(EC.visibility_of_element_located((By.XPATH, "//td[@class='row_name']//a")))
    logger.debug(f"The links are displayed: {element.is_displayed()}")
    logger.debug(element.is_displayed())
    result_list = get_element(driver)
    links = ["https:" + result_list[i].text for i in range(len(result_list))]    
    logger.debug(f"The links are: {links}")
    return links


def main():
    initialize_VPN(stored_settings=1)
    #IMPLEMENT NORD VPN SWITCHER TO BYPASS ISSUES, AFTER 20 PAGES
    #URL page1
    BASE_URL = "https://myip.ms/browse/sites/1/ownerID/376714/ownerID_A/1"
    rotate_VPN()
    #IMPLEMENT RANDOM NUMBER GENERATOR TO SCRAPE IPS FROM RANDOM PAGES, UP TO 9000
    #Create a set (cointainer with no duplicated values) to store the random integer number generated > the list will store the numbers > not to be re-used
    with open('list_randomPages_pulled.txt') as file:
        rnd_list = file.read().split(' ')
    #Make 10 dynamic, n defines the VPN rotation tool
    n = 0
    #List to store all the links
    url_dict = {}
    #pdf to store the table containing the links
    df_urls = pd.DataFrame()
    for _ in range(60):
        logger.debug(f"the count is: {n}")
        #The link will be randomly generated
        #Create a function to standardize random number generation which will be linked to the page to be scraped
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
        #Run the _run for a number of attempts to catch exceptions and try another time
        attempt = 0
        while attempt <= 3:
            try:
                #Create a function to standardize opening URL and GET element actions
                driver = get_option_url()
                page_state = driver.execute_script(
                'return document.readyState;'
                )
                page_state == 'complete'
                logger.debug(page_state)
                links = _run(driver,page_url)
                logger.debug(f"Links scraped at the first attempt: #{attempt}")
                attempt = 0
                break
            except:
                attempt += 1
                logger.debug(f"Either element not found or some issues, try another time, attempt #: {attempt}")
                driver = get_option_url()
                logger.debug('Re RUN...')
                links = _run(driver,page_url)
        logger.debug("Updating the Table containing the URLS")     
        url_dict[rnd_link] = links
        df_urls[rnd_link] = links        
        if n == 20:
            #Switch VPN to a different IP
            logger.debug("Switch IP address")
            rotate_VPN()
            n=0
        n+= 1
        driver.quit()
    return df_urls  
            
if __name__ == '__main__':
    time_to_append = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    filename = "table_urls_" + time_to_append + '.csv'
    cwd = Path.cwd() #setting current working directory
    output_folder = cwd / "shopify_urls"
    #Add parameters to control MAIN functions
    output =  main() 
    #with pd.ExcelWriter(cwd / filename) as writer:
    output.to_csv(output_folder / filename)
