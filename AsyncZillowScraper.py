import itertools, asyncio, random, time
from pyppeteer import launch
from utils import CHROMIUM_PATH
'''
NOTES:
 - I want the main() function to continously churn through different user agents every time it is ran or has an error in accessing the website
    - After let's say 5 attempts, whether success or not, rotate the user agent
'''
def RotateHeaders(): # Rotate Headers
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

    headers={ # Masks the request as a browser to avoid block from Zillow
        "accept-language": "en-US,en;q=0.9",
        "user-agent": random_user_agent,
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US;en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }

    return headers

def GetRandomProxy(): # Get all working proxies from the working_proxies.txt file
    with open('working_proxies.txt', 'r') as f:
        proxy = f.read().splitlines()
    return random.choice(proxy)

def RotateUserAgent(): # Rotates through User Agents by swapping proxies and headers; Returns a working proxy and random header
    
    headers = RotateHeaders() # Retrieve a random header
    proxy = GetRandomProxy() # Retrieve a working proxy

    return proxy, headers

async def main(URL_LINK, proxy, headers): # Main function to run the scraper, will take in all necessary parameters
    proxySOCKS5 = 'socks5://' + proxy
    proxyHTTPS = 'https://' + proxy
    try: # Pass as SOCKS5 proxy first, then as HTTP proxy if SOCKS5 fails
        browser = await launch({'headless': False,
                                'executablePath': CHROMIUM_PATH,
                                'args':[
                                    '--proxy-server=' + proxySOCKS5 ]})
        
        url = await browser.newPage()
        await url.setExtraHTTPHeaders(headers)
        await url.goto(URL_LINK)
        print("Success with SOCKS5 Proxy/Header Combo")

    except Exception as e:
        print(f'Error in main() with SOCKS5: {e}')
        await browser.close()
        try: # Retry the process with as HTTPS
            print('Trying as HTTPS Proxy...')
            browser = await launch({'headless': False,
                                'executablePath': CHROMIUM_PATH,
                                'args':[
                                    '--proxy-server=' + proxyHTTPS ]})
        
            url = await browser.newPage()
            await url.setExtraHTTPHeaders(headers)
            await url.goto(URL_LINK)
            print("Success with HTTPS Proxy/Header Combo")

        except Exception as e:
            print(f'Error in main() with HTTPS: {e}')
            proxy_new, headers_new = RotateUserAgent() # Retry the process with a new user agent
            await browser.close()
            print("Retrying with new Proxy and Headers")
            await main(URL_LINK, proxy_new, headers_new)

    finally:        
        await asyncio.sleep(random.randint(3,5)) # Random sleep time to avoid detection
        await browser.close()    

URL_LINK = 'https://webscraper.io/test-sites/e-commerce/allinone' # Once functions are created, this will link to whatever specific Zillow webpage we want to scrape
proxy, headers = RotateUserAgent()

asyncio.run(main(URL_LINK, proxy, headers))