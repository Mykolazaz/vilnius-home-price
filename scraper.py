from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import regex as re
import pandas as pd
import numpy as np

# Define max waiting time for element to appear
TIMEOUT = 5

# Define number of visits (visits pagesToVisit + 1)
PAGES_TO_VISIT = 104
 
MAIN_PAGE = 'https://www.aruodas.lt/'

cService = webdriver.ChromeService(executable_path='./webdriver/chromedriver')
driver = webdriver.Chrome(service=cService)

driver.get(MAIN_PAGE)

# Define waiting object
wait = WebDriverWait(driver, timeout=TIMEOUT)

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
columns = ['city', 'municipality', 'street', 'object_name', 'total_views', 'views_today', 'likes', 'price',
        'price_sq', 'house_number', 'flat_number', 'area', 'rooms', 'floor', 'total_floors', 'year',
        'object_type', 'building_type', 'heating', 'furnishing', 'energy_class', 'window_direction',
        'qualities', 'facilities', 'equipment', 'security', 'object_id', 'distance_kindergarden',
        'distance_school', 'distance_bus_stop', 'distance_shop', 'crimes', 'no2', 'kd10',
        'time_cathedral', 'time_train_station', 'distance_cathedral', 'distance_train_station', 'description', 'contact']
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

rowCounter = 0

for page in range(PAGES_TO_VISIT):

    # Collect all natural housing posts
    pageNaturalPosts = driver.find_elements(
        By.CSS_SELECTOR,
        'div.list-row-v2.object-row.selflat.advert a'
    )

    # Collect all unnatural housing posts
    pageUnnaturalPosts = driver.find_elements(
        By.CSS_SELECTOR,
        'table.advert-projects-table.type-id1 > tbody > tr > td:nth-child(1) > a'
    )

    pagePostLinks = []

    # Extract URLs from natural housing posts
    for a in pageNaturalPosts:
        href = a.get_attribute("href")
        # Ensure that URLs are unique and are not ads for a bank
        if href not in pagePostLinks and 'luminor' not in href:
            pagePostLinks.append(href)

    # Keep only URSs that come from clicking main part of posts
    pagePostLinks = list(filter(lambda x : re.search(r'^https://www\.aruodas\.lt/.*/\?search_pos=', x), pagePostLinks))

    # Extract URLs from unnatural housing posts
    for a in pageUnnaturalPosts:
        href = a.get_attribute("href")
        pagePostLinks.append(href)

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

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        # Collect object name
        objName = driver.find_element(By.CSS_SELECTOR, 'h1.obj-header-text').text

        # Collect object views
        objViews = driver.find_element(By.CSS_SELECTOR, 'div.obj-top-stats strong').text

        objLikes = driver.find_elements(By.CSS_SELECTOR, 'div.obj-top-stats > span')
        if len(objLikes) != 0:
            objLikes = objLikes[0].text

        # Collect and filter object price
        objPriceRaw = driver.find_element(By.CSS_SELECTOR, 'span.price-eur').text
        objPrice = re.sub(r'[^\d]', '', objPriceRaw)

        # Collect and filter object price per square meter
        objPriceSqRaw = driver.find_element(By.CSS_SELECTOR, 'span.price-per').text
        objPriceSq = re.sub(r'[^\d]', '', objPriceSqRaw)

        # Collect all object attribute names
        objDetailsElemName = driver.find_elements(By.CSS_SELECTOR, 'dl.obj-details dt:not([class])')
        objDetailsName = [re.sub(r':', '', elem.text) for elem in objDetailsElemName]
        objDetailsName = [re.sub(r'sk.', 'skaičius', elem) for elem in objDetailsName]
        # Map names in Lithuanian to names in English
        objDetailsName = list(map(detailsNameMap.get, objDetailsName))

        # Collect all object attribute values
        objDetailsElemValue = driver.find_elements(By.CSS_SELECTOR, 'dl.obj-details dd:not(.numai-v2)')
        objDetailsValue = [elem.text for elem in objDetailsElemValue]

        # Collect full object description
        objDescription = driver.find_element(By.CSS_SELECTOR, 'div#collapsedText').text

        objContact = None
        objContact1 = driver.find_elements(By.CSS_SELECTOR, 'div.contact-form-sidebar--phone > div > span.phone_item_0')
        objContact2 = driver.find_elements(By.CSS_SELECTOR, 'div.contact-form-sidebar--phone > div > span')
        if len(objContact1) != 0:
            objContact = objContact1[0].text
        elif len(objContact2) != 0:
            objContact = objContact2[0].text

        # Collect distance to important services
        objDistKinder = driver.find_elements(By.CSS_SELECTOR, 'div[data-category="darzeliai"] > div.distance-info > div.distance-value')
        if len(objDistKinder) != 0:
            objDistKinder = objDistKinder[0].text
        objDistSchool = driver.find_elements(By.CSS_SELECTOR, 'div[data-category="mokyklos"] > div.distance-info > div.distance-value')
        if len(objDistSchool) != 0:
            objDistSchool = objDistSchool[0].text
        objDistBusStop = driver.find_elements(By.CSS_SELECTOR, 'div[data-category="stoteles"] > div.distance-info > div.distance-value')
        if len(objDistBusStop) != 0:
            objDistBusStop = objDistBusStop[0].text 
        objDistShop = driver.find_elements(By.CSS_SELECTOR, 'div[data-category="parduotuves"] > div.distance-info > div.distance-value')
        if len(objDistShop) != 0:
            objDistShop = objDistShop[0].text


        objTimeCathedral = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#drive-times > div:nth-child(1) > div.destination-time.peak'))).text
        objDistCathedral = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#drive-times > div:nth-child(1) > div.destination-distance'))).text

        objTimeTrainStation = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#drive-times > div:nth-child(3) > div.destination-time.peak'))).text
        objDistTrainStation = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#drive-times > div:nth-child(3) > div.destination-distance'))).text

        objCrimes = driver.find_elements(By.XPATH, '//*[@id="advertStatisticHolder"]/div[3]/div[1]/span')
        objNO2 = driver.find_elements(By.XPATH, '//*[@id="advertStatisticHolder"]/div[1]/div[1]/div[1]/div[1]/span')
        objKD10 = driver.find_elements(By.XPATH, '//*[@id="advertStatisticHolder"]/div[1]/div[1]/div[2]/div[1]/span')
        if len(objCrimes) != 0:
            objCrimes = objCrimes[0].text
        if len(objNO2) != 0:
            objNO2 = objNO2[0].text
        if len(objKD10) != 0:
            objKD10 = objKD10[0].text
        

        # Create row in DataFrame
        allObjects.loc[rowCounter] = None

        # Insert object atrributes into DataFrame
        objNameList = list(map(str, re.split(',', objName)))

        allObjects.loc[rowCounter, 'city'] = objNameList[0]
        allObjects.loc[rowCounter, 'municipality'] = objNameList[1]
        allObjects.loc[rowCounter, 'street'] = objNameList[2]
        allObjects.loc[rowCounter, 'object_name'] = objNameList[3]

        allObjects.loc[rowCounter, 'total_views'] = re.findall(r'(\d+)/', objViews)[0]
        allObjects.loc[rowCounter, 'views_today'] = re.findall(r'/(\d+)', objViews)[0]

        if len(objLikes) != 0:
            allObjects.loc[rowCounter, 'likes'] = objLikes

        allObjects.loc[rowCounter, 'price'] = objPrice
        allObjects.loc[rowCounter, 'price_sq'] = objPriceSq

        for name, value in zip(objDetailsName, objDetailsValue):
            if name == 'area':
                areaNoUnits = re.sub(f' m²', '', value)
                areaNoComma = re.sub(f',', '.', areaNoUnits)
                allObjects.loc[rowCounter, name] = float(areaNoComma)
            elif name == 'furnishing':
                furnishingNoAd = re.sub(f'  \nSužinok apdailos kainą', '', value)
                allObjects.loc[rowCounter, name] = str(furnishingNoAd)
            else:
                allObjects.loc[rowCounter, name] = value
        
        if len(objDistKinder) != 0:
            allObjects.loc[rowCounter, 'distance_kindergarden'] = re.sub(r'[^\d]', '', objDistKinder)
        if len(objDistSchool) != 0:
            allObjects.loc[rowCounter, 'distance_school'] = re.sub(r'[^\d]', '', objDistSchool)
        if len(objDistBusStop) != 0:
            allObjects.loc[rowCounter, 'distance_bus_stop'] = re.sub(r'[^\d]', '', objDistBusStop)
        if len(objDistShop) != 0:
            allObjects.loc[rowCounter, 'distance_shop'] = re.sub(r'[^\d]', '', objDistShop)

        objTimeCathedral = re.search(r'(\d+)\s*-\s*(\d+)', objTimeCathedral)
        objTimeCathedral = np.mean(list(map(int, objTimeCathedral.groups())))

        allObjects.loc[rowCounter, 'time_cathedral'] = objTimeCathedral
        allObjects.loc[rowCounter, 'distance_cathedral'] = re.sub(r'[^\d|^\.]', '', objDistCathedral)

        objTimeTrainStation = re.search(r'(\d+)\s*-\s*(\d+)', objTimeTrainStation)
        objTimeTrainStation = np.mean(list(map(int, objTimeTrainStation.groups())))

        allObjects.loc[rowCounter, 'time_train_station'] = objTimeTrainStation
        allObjects.loc[rowCounter, 'distance_train_station'] = re.sub(r'[^\d|^\.]', '', objDistTrainStation)

        if len(objCrimes) != 0:
            allObjects.loc[rowCounter, 'crimes'] = re.sub(r'[^\d|^\.]', '', objCrimes)
        if len(objNO2) != 0:
            allObjects.loc[rowCounter, 'no2'] = re.sub(r'[^\d|^\.]', '', objNO2)
        if len(objKD10) != 0:
            allObjects.loc[rowCounter, 'kd10'] = re.sub(r'[^\d|^\.]', '', objKD10)

        allObjects.loc[rowCounter, 'description'] = objDescription

        if len(objContact1)!=0 or len(objContact2) != 0:
            allObjects.loc[rowCounter, 'contact'] = objContact

        # Print content to terminal
        print([objName, objViews, objPrice, objPriceSq])
        print(objDetailsName)
        print(f'{objDetailsValue}\n')

        rowCounter += 1

        driver.back()

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    nextPage = f'{MAIN_PAGE}butai/vilniuje/puslapis/{startPage-(page+1)}/?FOrder=AddDate'
    driver.get(nextPage)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")


# Save DataFrame to CSV
allObjects.to_csv('objects.csv', index=False)