import itertools, asyncio, random, time, httpx
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

def WriteProxy(proxy): # Writes a working proxy to the working_proxies.txt file

    with open('working_proxies.txt', 'a') as f:
        f.write(proxy + '\n')

def RotateUserAgent(): # Rotates through User Agents by swapping proxies and headers; Returns a working proxy and random header
    
    headers = RotateHeaders() # Retrieve a random header
    proxy = GetRandomProxy() # Retrieve a working proxy

    return proxy, headers

def SolveCaptcha(): # Function to solve captcha
    pass

async def TestProxies(URL_LINK): #Queues up proxy to be used in main() function. Runs along side main()
    while True:
        proxy = GetRandomProxy()
        proxy = f'socks5://{proxy}'

        try:
            async with httpx.AsyncClient(proxies = {"http://": proxy, "https://": proxy}) as client:
                r = await client.get(URL_LINK)
                if r.status_code == 200 or r.status_code == 403:
                    WriteProxy(proxy)
                    print(f'Proxy Works: {proxy} - Status: {r.status_code}')
        except Exception as e:
            print(f'Proxy: {proxy} failed! Status: {e}\n Retrying with new proxy...')

        await asyncio.sleep(random.randint(1,5)) # Test new proxy every 1-5 seconds    

async def main(URL_LINK, proxy, headers): # Main function to run the scraper, will take in all necessary parameters
    proxy = 'socks5://' + proxy
    
    try: # Pass as SOCKS5 proxy first, then as HTTP proxy if SOCKS5 fails
        browser = await launch({'headless': False,
                                'executablePath': CHROMIUM_PATH,
                                'args':[
                                    '--proxy-server=' + proxy]})
        
        url = await browser.newPage()
        await url.setExtraHTTPHeaders(headers)
        await url.goto(URL_LINK)

        print("Success with SOCKS5 Proxy/Header Combo")
        SolveCaptcha() # Function to solve captcha

    except Exception as e:
        print(f'Error in main(): {e}')
        proxy_new, headers_new = RotateUserAgent() # Retry the process with a new user agent
        await browser.close()
        print("Retrying with new Proxy and Headers")
        await main(URL_LINK, proxy_new, headers_new)
            
    finally:        
        await asyncio.sleep(random.randint(50,100)) # Random sleep time to avoid detection
        await browser.close()    

async def MainWrapper():
    URL_LINK = 'https://www.zillow.com/homedetails/705-Puesta-Del-Sol-Plz-Indialantic-FL-32903/43474044_zpid/' # Once functions are created, this will link to whatever specific Zillow webpage we want to scrape
    proxy, headers = RotateUserAgent()
    await asyncio.gather(main(URL_LINK, proxy, headers), TestProxies(URL_LINK))

            
asyncio.run(MainWrapper())