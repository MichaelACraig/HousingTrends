from utils import CHROMIUM_PATH
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import asyncio
import random
import csv

"""
- First iteration of file writing causes all the data from the first page to be written to all files; Fix later, not a big deal
"""

async def FetchWebpage(driver, URL): # Fetches the webpage using a headless browser w/ Selenium
    driver.get(URL)
    await asyncio.sleep(3) # Waits for the page to load
    r = driver.page_source
    return r

async def ScrapeTableData(cells, zipcode): # Helper function for CollectResultsData; Scrapes a given table's cells.

    for cell in cells:
            ACCOUNT_NUMBER = cell.find('button', class_='cssTextLink_Btn', attrs={'data-bind': 'text: account'})

            ADDRESS = cell.find('td', class_='cssCellMinWidth250 cssBorderRight multiline')
            OWNER = cell.find('td',class_='cssCellMinWidth250 cssBorderRight multiline classOwnerFormatted')
            PARCEL_ID = cell.find('td', class_='cssBorderRight force-one-line', attrs={'data-bind': 'text: parcelID'})
            SALE_DATE = cell.find('td', class_='cssBorderRight force-one-line', attrs={'data-bind': 'text: saleDateFormatted'})
            SALE_PRICE = cell.find('td', class_='cssRight cssBorderRight force-one-line right', attrs={'data-bind': 'text: salePrice'})
            MARKET_VALUE = cell.find('td', class_='cssRight cssBorderRight force-one-line right', style='display: none;', attrs={'data-bind': 'text: marketValue'})
            ACERAGE = cell.find('td', class_='cssBorderRight force-one-line', attrs={'data-bind':'text: acreage'})

            OFFICIAL_BOOK_PAGE = cell.find('td', class_='cssBorderRight force-one-line', attrs={'data-bind' : 'text: officialBookPage'}) # Useless data; Offical Book Page (idk what this is)
            LAND_USE_CODE = cell.find('td', class_='cssBorderRight force-one-line', attrs={'data-bind': 'text: landUseCode'})

            TAXING_DISTRICT = cell.find('td', class_='cssBorderRight force-one-line', attrs={'data-bind' : 'text: taxingDistrict'}) # Useless data; Taxing District
            SUBDIVISION = cell.find('td', class_='cssBorderRight force-one-line', attrs={'data-bind': 'text: subdivisionName'})

            TOTAL_BASE_AREA = cell.find('td', class_='cssBorderRight force-one-line', attrs={ 'data-bind': 'text: totalBaseArea'}) # Useless data; Total Base Area
            TOTAL_SUB_AREA = cell.find('td', class_='cssBorderRight force-one-line', attrs={ 'data-bind': 'text: totalSubArea'}) # Useless data; Total Sub Area
            YEAR_BUILT = cell.find('td', class_='cssCenter cssBorderRight force-one-line', attrs={'data-bind': 'text: yearBuilt'}) # Seems to be just a filler with no real data, all say 1980, maybe I'm wrong
            POOL = cell.find('td', class_='cssCenter cssBorderRight force-one-line', attrs={ 'data-bind': 'html: hasPool'}) # Useless data; Pool, Might be good future enrichment

            # Testing Text
            '''
            print('ACCOUNT NUMBER: ' + ACCOUNT_NUMBER.text)
            print("ADDRESS: " + ADDRESS.text)
            print("OWNER: " + OWNER.text)
            print("PARCEL ID: " + PARCEL_ID.text)
            print('SALE DATE: ' + SALE_DATE.text)
            print('SALE PRICE: ' + SALE_PRICE.text)
            print('MARKET VALUE: ' + MARKET_VALUE.text)
            print('LAND USE CODE: ' + LAND_USE_CODE.text)
            print('SUBDIVISION: ' + SUBDIVISION.text)
            print("Acerage: " + ACERAGE.text)
            print("Official Book Page: " + OFFICIAL_BOOK_PAGE.text)
            print("Taxing District: " + TAXING_DISTRICT.text)
            print("TBA: " + TOTAL_BASE_AREA.text)
            print("TSA: " + TOTAL_SUB_AREA.text)
            print("Year Built: " + YEAR_BUILT.text)
            print("Pool: " + POOL.text)
            '''
            
            # Write to CSV
            # Weird bug with windows storage to mac storage, fix later
            WINDOWS_STORAGE = f'Data Storage\\BCPAOData\\BCPAO_{zipcode}.csv'
            MAC_STORAGE = f'/Users/michaelcraig/Desktop/Projects/HousingTrends/Data Storage/BCPAOData/BCPAO_{zipcode}.csv'

            with open(MAC_STORAGE, 'a', newline='') as file:
                writer = csv.writer(file)
                if file.tell() == 0: # If file does not exist, write headers.
                    writer.writerow(['Address', 'Account Number', 'Owner', 'Parcel ID', 'Sale Date', 'Sale Price', 'Market Value', 'Land Use Code', 'Subdivision'])
                writer.writerow([ADDRESS.text, ACCOUNT_NUMBER.text, OWNER.text, PARCEL_ID.text, SALE_DATE.text, SALE_PRICE.text, MARKET_VALUE.text, LAND_USE_CODE.text, SUBDIVISION.text])
            await asyncio.sleep(1) # Avoids detection and overloading the website
              
async def CollectResultsData(driver, URL, zipcode, page):
    response = await FetchWebpage(driver, URL)
    soup = BeautifulSoup(response, 'html.parser')
    no_results = soup.find('div', id="divNoResultsFound", style='display: block;')
    
    if no_results is not None: # If no_results exist, return. We are at the end of the search.
        return

    # Else continue and scrape the table        
    table = soup.find('table', class_='table table-condensed table-striped table-hover table-bordered1; width: 100%;')
    cells = table.find_all('tr', class_='classResultsRow')

    if not cells:  # If there are no cells, there are no more pages to scrape
        return
    
    await ScrapeTableData(cells, zipcode) # Scrape the info
        
    next_page = page + 1
    next_page_URL = f'https://www.bcpao.us/PropertySearch/#/search/address={str(zipcode)}&activeonly=true&sortColumn=siteAddress&sortOrder=asc&page={next_page}' #Updates for next iteration

    await CollectResultsData(driver, next_page_URL, zipcode, next_page) # Pass updated functions and collect their results

async def ScrapeBatch(driver, zipcodes):
    tasks = []

    for zipcode in zipcodes:
        URL = f'https://www.bcpao.us/PropertySearch/#/search/address={zipcode}&activeonly=true&sortColumn=siteAddress&sortOrder=asc&page=1'
        task = CollectResultsData(driver, URL, zipcode, 1)
        tasks.append(task)

    await asyncio.gather(*tasks)

async def main():
    # Running into recursion error @ page 950. Fixed, but need to redo this batch later once all data is collected.
    redo_bin = [[32903, 32927, 32920, 32935, 32780],
                [32904, 32909, 32937, 32940, 32901],
                [32953, 32926, 32905, 32952, 32796],
                [32754, 32907, 32931, 32922, 32955],
                [32934]

                ] 
    
    do_bin =[
    [32902, 32906, 32911, 32910, 32919],
    [32912, 32924, 32923, 32932, 32936], 
    [32941, 32954, 32956, 32976, 32948],
    [32951, 32908]
    ]

    zipcodes = [[32775, 32781, 32783, 32959, 32899],
                [32950, 32949, 32925, 32782, 32815],
                
    ] # Clump zipcodes together for Parallelization; More efficient task running in async 

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    for batch in zipcodes:
        await ScrapeBatch(driver, batch)
        print(f'Finished batch {batch}')

    driver.quit()

async def main_wrapper():
    await main()        

asyncio.run(main_wrapper())    