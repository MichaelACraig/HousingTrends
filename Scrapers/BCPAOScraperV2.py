# Optimizing BCPAOScraper to access a different link: account url: https://www.bcpao.us/PropertySearch/#/account/(ACCOUNT NUMBER HERE)
# This can access ALL instances and store it under one .csv. Also might simplify complications I'm getting with collection via zipcodes

'''
Notes:
 - Scraper is complete

 Possible optimizations to run after first runtime:
    - Creating batches to track progress
'''
from utils import CHROMIUM_PATH
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd, asyncio, random, csv, re

async def FetchBrowser(driver, URL): # Fetches website; Returns page source
    driver.get(URL)
    await asyncio.sleep(1)
    r = driver.page_source
    return r

async def PopulateURLs(property_accounts): # Creates Batch of URLs to pass to headless browsers
    URL_List = []

    for account in property_accounts:
        URL = f'https://www.bcpao.us/PropertySearch/#/account/{account}'
        URL_List.append(URL)

    return URL_List    

async def Scrape(response, WINDOWS_DIR_ONE, WINDOWS_DIR_TWO): # Scrapes the data from URL
    soup = BeautifulSoup(response, 'html.parser')

    first_table = soup.find('div', class_="cssDetails_TopContainer cssTableContainer cssOverFlow_x cssCanReceiveFocus", role='region') # Account Data
    second_table = soup.find('table', class_='data-table cssWidth100') # Value Data
    # Transfer and Building Tables aren't applicable to the data collection

    # Initialize variables outside of clauses
    OWNER = ''
    MAIL_ADDRESS = ''
    SITE_ADDRESS = ''
    PARCEL_ID = ''
    TAXING_DISTRICT = ''
    EXEMPTIONS = ''
    PROPERTY_USE = ''
    ACERAGE = ''
    SITE_CODE = ''
    PLAT_BOOK = ''
    SUBDIVISION = ''
    DESCRIPTION = ''
        
    MARKETVAL_2021 = ''
    MARKETVAL_2022 = ''
    MARKETVAL_2023 = ''

    # If these tables exist, collect the data from them
    if first_table is not None: 
        layer_one = soup.find('div',class_='cssDetails_Top_Details')
        rows = layer_one.find_all('div', class_='cssDetails_Top_Row')

        for row in rows:
                layer_one = row.find('div',class_='cssDetails_Top_Cell_Data')

                if layer_one:
                    if layer_one.find('div', attrs={'data-bind': 'text: publicOwners'}):
                        OWNER = layer_one.find('div', attrs={'data-bind': 'text: publicOwners'}).text.strip()
                        continue
                    if layer_one.find('div', attrs={'data-bind': 'text: mailingAddress.formatted'}):
                        MAIL_ADDRESS = layer_one.find('div', attrs={'data-bind': 'text: mailingAddress.formatted'}).text.strip()
                        continue
                    if layer_one.find('div', attrs={'data-bind': 'text: siteAddressFormatted'}):
                        SITE_ADDRESS = layer_one.find('div', attrs={'data-bind': 'text: siteAddressFormatted'}).text.strip()
                        continue
                    if row.find('div', attrs={'data-bind':'if: exemptions().length == 0'}) or row.find('div',attrs={'data-bind': 'text: publicExemptions'}): # Might need an or clause for if exemptions length != 0
                        if row.find('div', attrs={'data-bind':'if: exemptions().length == 0'}):
                            EXEMPTIONS = row.find('div', attrs={'data-bind':'if: exemptions().length == 0'}).text.strip()
                            continue
                        else:
                            EXEMPTIONS = row.find('div',attrs={'data-bind': 'text: publicExemptions'}).text.strip()    
                            continue     

                if row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: parcelID'}, id='divDetails_Pid'):
                    PARCEL_ID = row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: parcelID'}, id='divDetails_Pid').text.strip()
                    continue

                if row.find('div', class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: publicTaxDistrict'}):
                    TAXING_DISTRICT = row.find('div', class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: publicTaxDistrict'}).text.strip()
                    continue
                    
                if row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: publicUseCode'}):
                    PROPERTY_USE = row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: publicUseCode'}).text.strip()
                    continue

                if row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: acreage'}):
                    ACERAGE = row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: acreage'}).text.strip()
                    continue                

                if row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: siteCodeDesc'}):
                    SITE_CODE = row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: siteCodeDesc'}).text.strip()
                    continue

                if row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: platBookPage'}):
                    PLAT_BOOK = row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: platBookPage'}).text.strip()
                    continue

                if row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: subdivisionName'}):
                    SUBDIVISION = row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: subdivisionName'}).text.strip()
                    continue

                if row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: legalDescription'}):
                    DESCRIPTION = row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: legalDescription'}).text.strip()
                    continue                

        if second_table is not None: # Needs to be in first_table clause because we won't know what the history is w/o the name
            MARKETVAL_2021 = second_table.find('td', attrs={'data-bind': 'text: marketVal'}).text.strip()
            MARKETVAL_2022 = second_table.find('td', attrs={'data-bind': 'text: marketVal1'}).text.strip()
            MARKETVAL_2023 = second_table.find('td', attrs={'data-bind': 'text: marketVal2'}).text.strip()

            '''
            # Test Prints
            print(OWNER)
            print(MAIL_ADDRESS)
            print(SITE_ADDRESS)
            print(PARCEL_ID)
            print(TAXING_DISTRICT)
            print(EXEMPTIONS)
            print(PROPERTY_USE)
            print(ACERAGE)
            print(SITE_CODE)
            print(PLAT_BOOK)
            print(SUBDIVISION)
            print(DESCRIPTION)     
            print(MARKETVAL_2021)
            print(MARKETVAL_2022)
            print(MARKETVAL_2023)
            '''

        # Write the values to .csv here
        with open(WINDOWS_DIR_ONE, 'a', newline='') as file_one:
            writer_one = csv.writer(file_one)
            if file_one.tell() == 0:
                writer_one.writerow(['Owner(s)', 'Mail Address', 'Site Address', 'Parcel ID', 'Taxing District','2023 Exemptions', 'Property Use', 'Acerage', 'Site Code','Plat Book/Page', 'Subdivision', 'Land Description', '2023 Market Value', '2022 Market Value', '2021 Market Value'])
            writer_one.writerow([OWNER,MAIL_ADDRESS,SITE_ADDRESS,PARCEL_ID,TAXING_DISTRICT,EXEMPTIONS,PROPERTY_USE,ACERAGE,SITE_CODE,PLAT_BOOK,SUBDIVISION,DESCRIPTION,MARKETVAL_2021,MARKETVAL_2022,MARKETVAL_2023])
        return
    
    # If table_one is missing, write the ID to the missing csv to comb through later
    if first_table is None:
        missing_layer_one = soup.find('div',id='divSearchDetails_Info', class_='cssSearchDetails_Panel cssPanelBorder_Top')
        missing_data = missing_layer_one.find('span', class_='spnDetailsRenum').text
        number = re.search(r'\d+', missing_data).group() # Pulls just the number from the string
        print(f'{number} holds no structured data! Placing in missing container...')

        with open(WINDOWS_DIR_TWO, 'a', newline='') as file_two:
            writer_two = csv.writer(file_two)
            if file_two.tell() == 0:
                writer_two.writerow(['ID'])
            writer_two.writerow([number])    
        return
    return
 
async def UpdateIDs(property_accounts):
    if property_accounts:  # Check if the list is not empty
        last_id = property_accounts[-1]  # Get the last ID
        property_accounts[0] = last_id + 1  # Set the first element to last_id + 1
        for i in range(1, len(property_accounts)):  # Update the rest of the list
            property_accounts[i] = property_accounts[0] + i
    return property_accounts  

async def main(property_accounts, driver):
    WINDOWS_DIR_ONE = 'Data Storage\\BCPAOData\\BCPAO_Data.csv'
    WINDOWS_DIR_TWO = 'Data Storage\\BCPAOData\\BCPAO_Data_Missing.csv'
    MAC_DIR = '' # Fill in when writing in MAC environment

    if property_accounts[0] == 3034724:
        print("We have reached the last element. Exiting...")
        return
    
    try:
        property_URLs = await PopulateURLs(property_accounts)

        for URL in property_URLs:
            response = await FetchBrowser(driver, URL)
            await Scrape(response, WINDOWS_DIR_ONE, WINDOWS_DIR_TWO)

        new_accounts = await UpdateIDs(property_accounts)
        await main(new_accounts, driver)

    except Exception as e:
        print(f'Error: {e}')
        # Need exception for whenever this is wrong, maybe just move on

async def main_wrapper():
    property_accounts = [2000001, 2000002, 2000003, 2000004, 2000005, 2000006, 2000007, 2000008, 2000009, 2000010]

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    
    try:
        await main(property_accounts, driver)
    finally:
        driver.quit()    

asyncio.run(main_wrapper())