from bs4 import BeautifulSoup
import pandas as pd
import requests
import itertools
import random
import certifi
import csv
import time

"""
Notes:
- Zillow has a CAPTCHA that needs to be bypassed after a certain amount of requests
- RotateProxy function is slow after first pass; Need to speed up later by labelling each proxy as HTTPS or SOCKS5. Not really a big deal tho so fix later.

"""
def RotateHeaders(): # Rotate headers to avoid being blocked by Zillow
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 YaBrowser/22.1.4.84 Yowser/2.5 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.56",
    ]

    # Randomly select a user agent
    random_user_agent = random.choice(user_agents)

    return random_user_agent

def GetProxies():
    with open('working_proxies.txt', 'r') as f:
        proxies = f.read().splitlines()
    return itertools.cycle(proxies)

def RotateProxy(url, proxies): # Rotate proxies to avoid being blocked by Zillow
        
        if url.startswith('/'): # Probably redundant, but just in case
            url = 'https://www.zillow.com' + url

        headers={ # Masks the request as a browser to avoid block from Zillow
        "accept-language": "en-US,en;q=0.9",
        "user-agent": RotateHeaders(),
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US;en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }
        proxy = next(proxies)

        formattedProxySOCKS5 = {
            'http': f'socks5://{proxy}',
            'https': f'socks5://{proxy}'
        }
        formattedProxyHTTPS = {
        'http': f'http://{proxy}',
        'https': f'https://{proxy}'
    }

        for proxy in proxies:
            try: # Try proxy as a SOCKS5 Input
                responseSOCKS5 = requests.get(url, headers=headers, proxies=formattedProxySOCKS5, verify=certifi.where(), timeout=10)

                if responseSOCKS5.status_code == 403: # If blocked, rotate proxy
                    with open('working_proxies.txt', 'a') as f:
                        f.write(proxy + '\n')

                    return RotateProxy(url, proxies)
                
                # Create a new text file with working proxies
                with open('working_proxies.txt', 'a') as f:
                    f.write(proxy + '\n')

                return responseSOCKS5
            
            except requests.exceptions.RequestException as e:
                print(f'Error with SOCKS5 proxy {proxy}: {e}\n Trying HTTPS...')

                try: # If SOCKS5 fails, try HTTPS
                    responseHTTPS = requests.get(url, headers=headers, proxies=formattedProxyHTTPS, verify=certifi.where(), timeout=10)

                    if responseHTTPS.status_code == 403: # If blocked, rotate proxy
                        with open('working_proxies.txt', 'a') as f:
                            f.write(proxy + '\n')

                        return RotateProxy(url, proxies)
                    
                    # Create a new text file with working proxies
                    with open('working_proxies.txt', 'a') as f:
                        f.write(proxy + '\n')

                    return responseHTTPS
                
                except requests.exceptions.RequestException as e:
                    print(f'Error with HTTPS proxy {proxy}: {e}')
                    return RotateProxy(url, proxies)

def ScrapeAgentURLS(zipcode, pageNumber, agentsList, proxies): # Scrape agents from Zillow in a given zipcode; Outputs a .csv file that checks for duplicates
    page = pageNumber

    # Access the Zillow website
    AGENT_URL = 'https://www.zillow.com/professionals/real-estate-agent-reviews/' + str(zipcode) + '/?page=' + str(page)
    print(AGENT_URL)

    response = RotateProxy(AGENT_URL, proxies)
    
    # Create a BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')

    layer1 = soup.find('div', class_="StyledLoadingMask-c11n-8-99-1__sc-1h8a6se-0 kKPGlw PageContent__BlockLoadingMask-sc-wiuawc-0 ezHpAR")
    layer2 = layer1.find('div', class_="StyledLoadingMaskContent-c11n-8-99-1__sc-1brcmz6-0")
    layer3 = layer2.find('section')
    layer4 = layer3.find('table', class_='StyledTable-c11n-8-99-1__sc-11t7upb-0 fITKUU')
    layer5 = layer4.find('tbody', class_="StyledTableBody-c11n-8-99-1__sc-f04mzl-0 gsoiWJ")

    agents = layer5.find_all('tr', class_="StyledTableRow-c11n-8-99-1__sc-65t1u6-0 hfWgOM")

    for agent in agents:
        agentURL = agent.find('a', class_="StyledTextButton-c11n-8-99-1__sc-1nwmfqo-0 dcAMHg")
        agentsList.add(agentURL['href'])

    # After loop is done, we now contain the href's to a specific agent page, update the page number and repeat the process
    page += 1

    if page > 25:
        return agentsList
    else:
        return ScrapeAgentURLS(zipcode, page, agentsList)    

def ScrapeAgentData(agentURL, proxies):
    # Access the Zillow website
    AGENT_URL = 'https://www.zillow.com' + agentURL

    response = RotateProxy(AGENT_URL, proxies)
    
    # Create a BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.prettify())
    # Retrieve agent data; Name, Phone, Email, Address
    AGENT_NAME = soup.find('h1', class_='Text-c11n-8-96-2__sc-aiai24-0 StyledHeading-c11n-8-96-2__sc-s7fcif-0 AVvvq').text
    AGENT_COMPANY = soup.find('div', class_='Text-c11n-8-96-2__sc-aiai24-0 kEiIUx').text
    print(AGENT_NAME)
    print(AGENT_COMPANY)

    AGENT_DATACARD = soup.find('div', class_='StyledCard-c11n-8-96-2__sc-1w6p0lv-0 kGKkgF') # Stores a ton of useful info; Pull rest of data from here

# Main
def main():

    proxies = GetProxies()
    ScrapeAgentData('/profile/John-DeMarco/', proxies)
    
    """    
    zipcodes = [32907,
    32940,
    32955,
    32935,
    32780,
    32904,
    32909,
    32937,
    32927,
    32901,
    32953,
    32926,
    32905,
    32952,
    32796,
    32934,
    32922,
    32931,
    32903,
    32908,
    32754,
    32951,
    32976,
    32920,
    32948,
    32950,
    32949,
    32925,
    32782,
    32815,
    32775,
    32781,
    32783,
    32959,
    32899,
    32902,
    32906,
    32911,
    32910,
    32919,
    32912,
    32924,
    32923,
    32932,
    32936,
    32941,
    32954,
    32956]

    page = 1
    agentsSet = set()

    print(ScrapeAgentURLS(32903, page, agentsSet))

    for zipcode in zipcodes:
        for agent in ScrapeAgentURLS(zipcode, page, agentsSet):
            ScrapeAgentData(agent)
    """
if __name__ == "__main__":
    main()    