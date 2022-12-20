from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from twocaptcha import TwoCaptcha

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("detach", True)

browser = webdriver.Chrome(options=options, executable_path=r"C:\Users\R_Giu\RPA\fiverr\chromedriver.exe")
browser.get("https://2captcha.com/demo/normal")

captcha = browser.find_element(By.CLASS_NAME, "_17bwEOs9gv8ZKqqYcEnMuQ")
captcha_img = captcha.screenshot("captchas/captcha.png")

api_key = os.getenv("APIKEY_2CAPTCHA", "186ae58c723e40dff69ed17b0b04b652")
solver = TwoCaptcha(api_key)

try:
    result = solver.normal("captchas/captcha.png")
except Exception as e:
    print(e)
else:
    code = result['code']
    
print(code)