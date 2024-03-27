# Optimizing BCPAOScraper to access a different link: account url: https://www.bcpao.us/PropertySearch/#/account/(ACCOUNT NUMBER HERE)
# This can access ALL instances and store it under one .csv. Also might simplify complications I'm getting with collection via zipcodes
from utils import CHROMIUM_PATH
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd, asyncio, random, csv

async def Fetch(driver, URL): # Fetches website
    driver.get(URL)
    await asyncio.sleep(1)
    r = driver.page_source
    return r


