import time
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


def detect_verification(driver):
    wait = WebDriverWait(driver, timeout=30, ignored_exceptions=[TimeoutException])
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="captcha_submit"]'))).click()
    except:
        logger.debug('Human verification not present')
    '''
        try:
        element_popup = driver.find_element(By.XPATH,'//*[@id="captcha_submit"]')
        if element_popup.is_displayed():
                element_popup.click()
        try:
            element_popup2 = driver.find_element(By.XPATH, '//*[@id="captcha_submit"]')
            if element_popup2.is_displayed():
                element_popup2.click()
        except Exception as e:
                logger.info('Human Verification detected and avoided')
    except Exception as e:
            logger.info(f'Human Verification not present')
    '''


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
    wait = WebDriverWait(driver, timeout=30, ignored_exceptions=[TimeoutException])
    #driver.find_elements(By.XPATH, "//td[@class='row_name']//a")
    wait.until(EC.presence_of_element_located((By.XPATH,"//td[@class='row_name']//a")))
     
def get_rand_int():
    return randint(1, 8146)

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
    with open('list_random_pages.txt') as file:
        rnd_list = file.read().split(' ')
    #Make 10 dynamic
    n = 0
    #list of columns containing the rnd link being pulled out
    columns = []
    df_ = pd.DataFrame()
    with pd.ExcelWriter(Path.cwd() / 'test_excel_new.xlsx', engine='xlsxwriter') as xfile:
        for _ in range(50):
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
            options = uc.ChromeOptions()
            #Define the driver
            driver = uc.Chrome(options=options)
            #driver.set_page_load_timeout(60)
            #driver.set_script_timeout(60)
            #Define the wait
            logger.info(f"Opening the URL page: {page_url}")
            driver.get(page_url)
            #wait = get_wait_element(driver)
            #Improve detect verification
            detect_verification(driver)
            #driver.implicitly_wait(2)
            logger.debug(driver.current_url)
            #driver.implicitly_wait(3)
            result_list = get_element(driver)
            logger.debug(len(result_list))
            links = get_links(result_list)
            logger.debug(f"The links are: {links}")
            #Create a dictionary to store the links, the keys will be the number of page
            #Don't want to scrape the same page
            url_dict[rnd_link] = links
            df_urls[rnd_link] = links
            #Appending new page to columns list
            df_urls.to_excel(xfile, sheet_name='sheet1', mode='a')
            #writer.write('\n'.join(links))
            #update the count > maybe not necessary, can use i instead
            if n == 10:
                #Switch VPN to a different IP
                logger.debug("Switch IP address")
                rotate_VPN()
                n=0
            n+= 1
            driver.quit()
    return df_urls  
            
if __name__ == '__main__':
    time_to_append = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = "table_urls_" + time_to_append + '.xlsx'
    cwd = Path.cwd() #setting current working directory
    output =  main() 
    with pd.ExcelWriter(cwd / filename) as writer:
        output.to_excel(writer, sheet_name='sheet1')
    '''
        table = pd.DataFrame()
    list_rnd_pulled = output.keys()
    for i,v in output.items():
        table[i] = v
    time_to_append = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    cwd = Path.cwd()
    filename = "table_urls_" + time_to_append + '.xlsx'
    table.to_excel(cwd / filename)
    '''
