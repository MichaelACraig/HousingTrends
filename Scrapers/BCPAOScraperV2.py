# Optimizing BCPAOScraper to access a different link: account url: https://www.bcpao.us/PropertySearch/#/account/(ACCOUNT NUMBER HERE)
# This can access ALL instances and store it under one .csv. Also might simplify complications I'm getting with collection via zipcodes

'''
Notes:
 - Create in async to reduce overall runtime of the program; we have over 300k instances to go through, if we can run 10 batches, good, but 5 is fine.
   ~ Create a multiple variables based off a single variable so it updates all instances correctly when running. Might need to be recrusive? Unsure.

 - Scraper is based off of this URL: https://www.bcpao.us/PropertySearch/#/account/(ACCOUNT NUMBER HERE)
    ~ Starts at 2000001. Ends at 3034724

 - Cannot use an AI Agent via OpenAI to scrape data; Too many tokens. 1.034723 Million Properties which converts a token a property
'''
from utils import CHROMIUM_PATH
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd, asyncio, random, csv

def FetchBrowser(driver, URL): # Fetches website; Returns page source
    driver.get(URL)
    #await asyncio.sleep(1)
    r = driver.page_source
    return r

async def PopulateURLs(property_accounts): # Creates Batch of URLs to pass to headless browsers
    URL_List = []

    for account in property_accounts:
        URL = f'https://www.bcpao.us/PropertySearch/#/account/{account}'
        URL_List.append(URL)

    return URL_List    

def Scrape(response): # Scrapes the data from URL
    soup = BeautifulSoup(response, 'html.parser')

    first_table = soup.find('div', class_="cssDetails_TopContainer cssTableContainer cssOverFlow_x cssCanReceiveFocus", role='region') # Account Data
    second_table = soup.find('table', class_='data-table cssWidth100') # Value Data
    third_table = soup.find('table', class_='tSalesTransfers') # Sales and Transfers Data
    # There is a fourth table for building data, but I don't think it's very applicable to what we're predicting

    if first_table is not None: # If these tables exist, collect the data from them
        layer_one = soup.find('div',class_='cssDetails_Top_Details')
        rows = layer_one.find_all('div', class_='cssDetails_Top_Row')
        for row in rows:
            print(row.prettify())
            print('----------------------------------------------------------------')
        # Initialize variables outside the loop
        OWNER = ""
        MAIL_ADDRESS = ""
        SITE_ADDRESS = ""
        PARCEL_ID = ""
        TAXING_DISTRICT = ""
        EXEMPTIONS = ""
        PROPERTY_USE = ""
        ACERAGE = ""
        SITE_CODE = ""
        PLAT_BOOK = ""
        SUBDIVISION = ""
        DESCRIPTION = ""

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

                if row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: acerage'}):
                    ACERAGE = row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: acerage'}).text.strip()
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
                    SUBDIVISION = row.find('div',class_='cssDetails_Top_Cell_Data', attrs={'data-bind':'text: legalDescription'}).text.strip()
                    continue                

        print("OWNER:", OWNER)
        print("SITE_ADDRESS:", SITE_ADDRESS)
        print("MAIL_ADDRESS:", MAIL_ADDRESS)
        print("PARCEL_ID:", PARCEL_ID)
        print("TAXING_DISTRICT:", TAXING_DISTRICT)
        print("EXEMPTIONS:", EXEMPTIONS)
        print("PROPERTY_USE:", PROPERTY_USE)
        print("ACERAGE:", ACERAGE)
        print("SITE_CODE:", SITE_CODE)
        print("PLAT_BOOK:", PLAT_BOOK)
        print("SUBDIVISION:", SUBDIVISION)
        print("DESCRIPTION:", DESCRIPTION)

        #if second_table is not None:
        
        #if third_table is not None:

    # Place functionality for first_table not existing here;
            
async def main():
    property_accounts = [2000001, 2000002, 2000003, 2000004, 2000005, 2000006, 2000007, 2000008, 2000009, 2000010]
    WINDOWS_DIR_ONE = 'Data Storage\\BCPAOData\\BCPAO_Data.csv'
    WINDOWS_DIR_TWO = 'Data Storage\\BCPAOData\\BCPAO_Data_Missing.csv'
    MAC_DIR = '' # Fill in when writing in MAC environment

    '''
    with open(WINDOWS_DIR_TWO, 'a', newline='') as file_two: # Place this code in Scrape() function later
        writer_two = csv.writer(file_two)
        if file_two.tell() == 0:
            writer_one.writerow(['Owner(s)', 'Mail Address', 'Site Address', 'Parcel ID', 'Taxing District','2023 Exemptions', 'Property Use', 'Acerage', 'Site Code','Plat Book/Page', 'Subdivision', 'Land Description', '2023 Market Value', '2022 Market Value', '2021 Market Value'])
    '''

    property_URLs = await PopulateURLs(property_accounts)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    
    for URL in property_URLs:
        response = await FetchBrowser(driver, URL)
        await Scrape(response)

async def main_wrapper():
    await main()

#asyncio.run(main_wrapper())

'''----Test Environment Below----'''

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)

URL = 'https://www.bcpao.us/PropertySearch/#/account/2000001'
WINDOWS_DIR_ONE = 'Data Storage\\BCPAOData\\BCPAO_Data.csv'
WINDOWS_DIR_TWO = 'Data Storage\\BCPAOData\\BCPAO_Data_Missing.csv'
  
response = FetchBrowser(driver, URL)
Scrape(response)