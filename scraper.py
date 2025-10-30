from selenium import webdriver
from selenium.webdriver.common.by import By
import time

cService = webdriver.ChromeService(executable_path='./webdriver/chromedriver')

driver = webdriver.Chrome(service=cService)

driver.get('https://www.aruodas.lt/')

time.sleep(1)

# Decline all cookies
driver.find_element(By.ID, 'onetrust-reject-all-handler').click()

# Open municipality radio menu
driver.find_elements(By.ID, 'display_FRegion')[0].click()

# Click on city Vilnius
driver.find_element(By.CSS_SELECTOR, 'label.dropDownLabel[for="input_FRegion_461"]').click()

# Click 'Search' button
driver.find_element(By.ID, 'buttonSearchForm').click()

# Click advert list order button and choose the second option
driver.find_element(By.XPATH, '//*[@id="changeListOrder"]/option[2]').click()

# Go to the last page
driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div[1]/div[9]/a[7]').click()

time.sleep(10)



