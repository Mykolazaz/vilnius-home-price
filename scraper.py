from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import regex as re

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

time.sleep(1)

# Click 'Search' button
driver.find_element(By.ID, 'buttonSearchForm').click()

time.sleep(1)

# Click advert list order button and choose the second option
driver.find_element(By.XPATH, '//*[@id="changeListOrder"]/option[2]').click()

time.sleep(1)

# Go to the last page
driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div[1]/div[9]/a[7]').click()

# Collect all housing posts
pagePosts = driver.find_elements(
    By.CSS_SELECTOR,
    'div.list-row-v2.object-row.selflat.advert a'
)

pagePostLinks = []

# Extract URLs from housing posts
for a in pagePosts:
    href = a.get_attribute("href")
    # Ensure that URLs are unique and are not ads for a bank
    if href not in pagePostLinks and 'luminor' not in href:
        pagePostLinks.append(href)

# Keep only URSs that come from clicking main part of posts
pagePostLinks = list(filter(lambda x : re.search(r'^https://www\.aruodas\.lt/.*/\?search_pos=', x), pagePostLinks))

# Go through all fitered URLs
for url in pagePostLinks:
    driver.get(url)

    # Namo numeris
    # Buto numeris
    # Plotas
    # Aukštas
    # Aukštų skaičius
    # Metai (2001, '1993 statyba, 2011 renovacija')
    # Objektas ()
    # Pastato tipas
    # Šildymas
    # Įrengimas
    # Pastato energijos suvartojimo klasė
    # Ypatybės (Varžytinės/aukcionas)
    # Papildomos patalpos
    # Papildoma įranga (Skalbimo mašina/Su baldais/Šaldytuvas)
    # Apsauga (Šarvuotos durys/Signalizacija)

    objName = driver.find_element(By.CSS_SELECTOR, 'h1.obj-header-text').text

    objViews = driver.find_element(By.CSS_SELECTOR, 'div.obj-top-stats strong').text

    objPrice = driver.find_element(By.CSS_SELECTOR, 'span.price-eur').text

    objPriceSq = driver.find_element(By.CSS_SELECTOR, 'span.price-per').text

    objDetailsElemName = driver.find_elements(By.CSS_SELECTOR, 'dl.obj-details dt:not([class]')
    objDetailsName = [elem.text for elem in objDetailsElemName]

    objDetailsElemValue = driver.find_elements(By.CSS_SELECTOR, 'dl.obj-details dd span.fieldValueContainer')
    objDetailsValue = [elem.text for elem in objDetailsElemValue]

    print(objDetailsName)
    print(objDetailsValue)

    print([objName, objViews, objPrice, objPriceSq])

    time.sleep(2)

    driver.back()

    time.sleep(2)

time.sleep(5)