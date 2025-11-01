from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import regex as re
import pandas as pd

cService = webdriver.ChromeService(executable_path='./webdriver/chromedriver')
driver = webdriver.Chrome(service=cService)

driver.get('https://www.aruodas.lt/')

timeout = 5
wait = WebDriverWait(driver, timeout=timeout)

# Define number of visits (visits pagesToVisit + 1)
pagesToVisit = 2

# Decline all cookies
wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))).click()

# Open municipality radio menu
wait.until(EC.element_to_be_clickable((By.ID, 'display_FRegion'))).click()

# Click on city Vilnius
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'label.dropDownLabel[for="input_FRegion_461"]'))).click()

# Click 'Search' button
wait.until(EC.element_to_be_clickable((By.ID, 'buttonSearchForm'))).click()

# Click advert list order button and choose the second option
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="changeListOrder"]/option[2]'))).click()

# Go to the last page
driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div[1]/div[9]/a[7]').click()

startPage = int(driver.find_element(By.CSS_SELECTOR, 'a.active-page').text)

# Define DataFrame
columns = ['city', 'manucipality', 'street', 'object_name', 'total_views', 'views_today', 'price',
        'price_sq', 'house_number', 'flat_number', 'area', 'rooms',
        'floor', 'total_floors', 'year', 'object_type', 'building_type', 'heating', 'furnishing',
        'energy_class', 'window_direction', 'qualities', 'facilities', 'equipment', 'security']
allObjects = pd.DataFrame(columns=columns)

detailsNameMap = {'Namo numeris':'house_number',
                        'Buto numeris':'flat_number',
                        'Unikalus daikto numeris (RC numeris)': 'object_id',
                        'Plotas':'area',
                        'Kambarių skaičius':'rooms',
                        'Aukštas':'floor',
                        'Aukštų skaičius':'total_floors',
                        'Metai':'year',
                        'Objektas':'object_type',
                        'Pastato tipas':'building_type',
                        'Šildymas':'heating',
                        'Įrengimas':'furnishing',
                        'Langų orientacija':'window_direction',
                        'Pastato energijos suvartojimo klasė':'energy_class',
                        'Ypatybės':'qualities',
                        'Papildomos patalpos':'facilities',
                        'Papildoma įranga':'equipment',
                        'Apsauga':'security'}

for page in range(pagesToVisit):

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
    for i, url in enumerate(pagePostLinks):
        driver.get(url)

        # Namo numeris
        # Buto numeris
        # Unikalus daikto numeris (RC numeris)
        # Plotas
        # Kambarių skaičius
        # Aukštas
        # Aukštų skaičius
        # Metai (2001, '1993 statyba, 2011 renovacija')
        # Objektas
        # Pastato tipas
        # Šildymas
        # Įrengimas
        # Langų orientacija
        # Pastato energijos suvartojimo klasė
        # Ypatybės (Varžytinės/aukcionas)
        # Papildomos patalpos
        # Papildoma įranga (Skalbimo mašina/Su baldais/Šaldytuvas)
        # Apsauga (Šarvuotos durys/Signalizacija)

        # Collect object name
        objName = driver.find_element(By.CSS_SELECTOR, 'h1.obj-header-text').text

        # Collect object views
        objViews = driver.find_element(By.CSS_SELECTOR, 'div.obj-top-stats strong').text

        # Collect and filter object price
        objPriceRaw = driver.find_element(By.CSS_SELECTOR, 'span.price-eur').text
        objPrice = re.sub(r'[^\d]', '', objPriceRaw)

        # Collect and filter object price per square meter
        objPriceSqRaw = driver.find_element(By.CSS_SELECTOR, 'span.price-per').text
        objPriceSq = re.sub(r'[^\d]', '', objPriceSqRaw)

        # Collect all object attribute names
        objDetailsElemName = driver.find_elements(By.CSS_SELECTOR, 'dl.obj-details dt:not([class]')
        objDetailsName = [re.sub(r':', '', elem.text) for elem in objDetailsElemName]
        objDetailsName = [re.sub(r'sk.', 'skaičius', elem) for elem in objDetailsName]
        # Map names in Lithuanian to names in English
        objDetailsName = list(map(detailsNameMap.get, objDetailsName))


        # Collect all object attribute values
        objDetailsElemValue = driver.find_elements(By.CSS_SELECTOR, 'dl.obj-details dd:not(.numai-v2)')
        objDetailsValue = [elem.text for elem in objDetailsElemValue]

        # Create row in DataFrame
        allObjects.loc[page + i] = None

        # Insert object atrributes into DataFrame
        objNameList = list(map(str, re.split(',', objName)))

        allObjects.loc[page + i, 'city'] = objNameList[0]
        allObjects.loc[page + i, 'manucipality'] = objNameList[1]
        allObjects.loc[page + i, 'street'] = objNameList[2]
        allObjects.loc[page + i, 'object_name'] = objNameList[3]

        allObjects.loc[page + i, 'total_views'] = re.findall(r'(\d+)/', objViews)[0]
        allObjects.loc[page + i, 'views_today'] = re.findall(r'/(\d+)', objViews)[0]
        allObjects.loc[page + i, 'price'] = objPrice
        allObjects.loc[page + i, 'price_sq'] = objPriceSq

        for name, value in zip(objDetailsName, objDetailsValue):
            if name == 'area':
                areaNoUnits = re.sub(f' m²', '', value)
                areaNoComma = re.sub(f',', '.', areaNoUnits)
                allObjects.loc[page + i, name] = float(areaNoComma)
            elif name == 'furnishing':
                furnishingNoAd = re.sub(f'  \nSužinok apdailos kainą', '', value)
                allObjects.loc[page + i, name] = str(furnishingNoAd)
            else:
                allObjects.loc[page + i, name] = value

        # Print content to terminal
        print([objName, objViews, objPrice, objPriceSq])
        print(objDetailsName)
        print(f'{objDetailsValue}\n')

        driver.back()

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    
    nextPage = f'https://www.aruodas.lt/butai/vilniuje/puslapis/{startPage-(page+1)}/?FOrder=AddDate'
    driver.get(nextPage)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")


# Save DataFrame to CSV
allObjects.to_csv('objects.csv', index=False)

time.sleep(5)