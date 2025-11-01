from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import regex as re
import pandas as pd

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
    allObjects.loc[i] = None

    # Insert object atrributes into DataFrame
    objNameList = re.split(',', objName)

    allObjects.loc[i, 'city'] = objNameList[0]
    allObjects.loc[i, 'manucipality'] = objNameList[1]
    allObjects.loc[i, 'street'] = objNameList[2]
    allObjects.loc[i, 'object_name'] = objNameList[3]

    allObjects.loc[i, 'total_views'] = re.findall(r'(\d+)/', objViews)[0]
    allObjects.loc[i, 'views_today'] = re.findall(r'/(\d+)', objViews)[0]
    allObjects.loc[i, 'price'] = objPrice
    allObjects.loc[i, 'price_sq'] = objPriceSq

    for name, value in zip(objDetailsName, objDetailsValue):
        if name == 'area':
            areaNoUnits = re.sub(f' m²', '', value)
            areaNoComma = re.sub(f',', '.', areaNoUnits)
            allObjects.loc[i, name] = float(areaNoComma)
        elif name == 'furnishing':
            furnishingNoAd = re.sub(f'  \nSužinok apdailos kainą', '', value)
            allObjects.loc[i, name] = str(furnishingNoAd)
        else:
            allObjects.loc[i, name] = value

    # Print content to terminal
    print([objName, objViews, objPrice, objPriceSq])
    print(objDetailsName)
    print(f'{objDetailsValue}\n')

    time.sleep(2)

    driver.back()

    time.sleep(2)

# Save DataFrame to CSV
allObjects.to_csv('objects.csv', index=False)

time.sleep(5)