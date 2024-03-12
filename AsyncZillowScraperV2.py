import itertools, asyncio, random, time, httpx
from pyppeteer import launch
from utils import CHROMIUM_PATH
'''
NOTES:
 1. Main() should churn through proxies and headers until it successfully accesses the page
    1b. TestProxies() Should be testing proxies and appending them to working_proxies while main() is running
 2. Main() should then check for CAPTCHA and solve it if necessary. Move on if solved, retry if not
 3. After access, whichever functions are created will be called to scrape the data
 4. If the page is closed, main should try to reopen it twice before moving on to the next proxy and headers

 
- To Do:
 - Ask ChatGPT how I can optimize. Something about not creating/deleting a new browser instance every time I want to access a page/url sparked my interest

 - To make proxy churning more clean/effective, use a stack populated by working_proxies.txt and when it's empty, append working_proxies.txt to it again
    - This will allow for more efficient use because working_proxies.txt is consistently being updated with new working proxies via async function
 
 - Had a problem with headers, might need to rotate referers and cookies to avoid detection; Test later
    - Swap user_agents list with those that match the header arguments currently implemented

 - Write out a pipeline for doing Webscraping in the future; This will help me understand the process and what I need to do to make it work
    - Also can make a YT Video on it later :)      
'''
async def RotateHeaders(): # Rotate Headers
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        # Add more user agents as needed
    ]

    # Randomly select a user agent
    random_user_agent = random.choice(user_agents)

    headers={ # Masks the request as a browser to avoid block from Zillow
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'x-amz-continuous-deployment-state=AYABeFegd1XC6ZJHS%2F4Zp2hhc+UAPgACAAFEAB1kM2Jsa2Q0azB3azlvai5jbG91ZGZyb250Lm5ldAABRwAVRzA3MjU1NjcyMVRZRFY4RDcyVlpWAAEAAkNEABpDb29raWUAAACAAAAADBJLFfdHx+%2FzDJQo7AAwECJRMQlibzvMD0pSwutq5En6+MZfNVS+sbgxEimgYvW5lJH+ZgRjta2vL+w6KrgbAgAAAAAMAAQAAAAAAAAAAAAAAAAAADKuroLuivW7NzwunGlCjo%2F%2F%2F%2F%2F%2FAAAAAQAAAAAAAAAAAAAAAQAAAAy%2FTC2sm+B+FmCPpK5btls3re5MpUUB6Pp8Lxpf; zguid=24|%24f63fd8c8-4b77-443b-a6fc-da4043e668e4; zjs_anonymous_id=%22f63fd8c8-4b77-443b-a6fc-da4043e668e4%22; zjs_user_id=null; zg_anonymous_id=%2273183099-5a6a-4dd0-b774-50e1436704b9%22; _ga=GA1.2.104404930.1708182956; _pxvid=72a5425a-cda7-11ee-87bb-e71b77077129; _gcl_au=1.1.1283926456.1708182958; __gads=ID=e470cbf57d97745d:T=1708182957:RT=1708182957:S=ALNI_ManGMVMWhPTS-lDfJyMd98PUxNtOA; __gpi=UID=00000dcab728ffa8:T=1708182957:RT=1708182957:S=ALNI_MbBaAl9vDIU6tBy7sQ32tFGK8NUug; __eoi=ID=e48a34aeea74fa70:T=1708182957:RT=1708182957:S=AA-Afjas5D575OPvms25nYKXHctn; _pin_unauth=dWlkPU5tTmpPV0kxTVdZdFl6ZzBNUzAwT1ROaUxUa3hPRGN0WXpZMVpEUTROV1l3TTJGbQ; _fbp=fb.1.1708182958414.510054691; __pdst=6175ad7d68fa49bd91ab2a0ceb7f4bfe; optimizelyEndUserId=oeu1709782678067r0.2643757111219096; zgcus_aeut=AEUUT_165f0501-dc34-11ee-8a62-1640c131954c; zgcus_aeuut=AEUUT_165f0501-dc34-11ee-8a62-1640c131954c; _cs_c=0; _gac_UA-21174015-56=1.1709920443.CjwKCAiAi6uvBhADEiwAWiyRdicxOhpFvWlhz7hceWXhuxKb767Bc-I2gYuatpau38DHulZqnSga4BoCT-4QAvD_BwE; _gcl_aw=GCL.1709920445.CjwKCAiAi6uvBhADEiwAWiyRdicxOhpFvWlhz7hceWXhuxKb767Bc-I2gYuatpau38DHulZqnSga4BoCT-4QAvD_BwE; zgsession=1|3d14d7ff-62b8-4e0e-8693-c11a4440ebf6; _gid=GA1.2.1234669717.1710171293; pxcts=e83620c2-dfbc-11ee-9113-ed1823c505d2; DoubleClickSession=true; _clck=2htskj%7C2%7Cfjz%7C0%7C1508; _hp2_id.1215457233=%7B%22userId%22%3A%227892271171865068%22%2C%22pageviewId%22%3A%227840958062775579%22%2C%22sessionId%22%3A%228310128663611957%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _cs_id=e7c34e7b-2aff-afaf-e541-e47e87781bce.1709782797.7.1710175937.1710175837.1.1743946797000.1; _hp2_props.1215457233=%7B%22Contentsquare%20Replay%22%3A%22https%3A%2F%2Fapp.contentsquare.com%2Fquick-playback%2Findex.html%3Fpid%3D3747%26uu%3De7c34e7b-2aff-afaf-e541-e47e87781bce%26sn%3D7%26pvid%3D2%26recordingType%3Dcs%26vd%3Dhe%22%7D; g_state={"i_p":1710788657514,"i_l":3}; JSESSIONID=DB5CB98D7056C06E180550C288AF88A1; x-amz-continuous-deployment-state=AYABeLkllz7ybF2BjDv%2FsgjKnnQAPgACAAFEAB1kM2Jsa2Q0azB3azlvai5jbG91ZGZyb250Lm5ldAABRwAVRzA3MjU1NjcyMVRZRFY4RDcyVlpWAAEAAkNEABpDb29raWUAAACAAAAADJHHXYeCqxLj8MWZwQAwOL0tTUAbSUMx7N8Sb%2FJ9kwa6Nwaw68oBH6otvqxBrxIa6GL1BXE3dvSSBE+Gczj0AgAAAAAMAAQAAAAAAAAAAAAAAAAAAPZW5NPjwzXnQXDgyAL0aKL%2F%2F%2F%2F%2FAAAAAQAAAAAAAAAAAAAAAQAAAAy6xAzBwQYC4u0X9z6GhFVFMJfuhHSbFjLyLeyAfuhHSbFjLyLeyA==; search=6|1712775914134%7Cregion%3Dindialantic-fl%26rect%3D28.124474%252C-80.557675%252C28.076494%252C-80.592387%26disp%3Dmap%26mdm%3Dauto%26listPriceActive%3D1%26fs%3D1%26fr%3D0%26mmm%3D1%26rs%3D0%26ah%3D0%09%0952625%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Afalse%7D%09%09%09%09%09; _px3=1f03fda0bd2c901944b9afe1b4cac67c7ef242494a72f761028fb53fa954c3f1:ZYXK3cljWmsAIMuPFe2aGrlXJILyWuv0Q/ylh9h0qaC5m1JI/FjhY+T3m2hxaepoLU2V9SvSdYpiKkLEF8yttw==:1000:K3BB1H2UK15xrhcWckOJXMumFltsDh4lO0MWXsjkHXgCsDSonTm1RPvKwxZ6wdNRwLQ5nePt+gsg3O4ORD+qM5HbF6TSUTu3q+rRn4SyaI/2gbZS0d6BycnssU8vOrWazQpzxTFlvB5XZgyEoVgXOnpYr6XvnAyhsiHLJhm1krROmVai+eU3cz+1YhW3n34AbHXVRH2ljkkTCJ7rqcVUlMmjBpm1OQQwWR6lOx2ovGI=; AWSALB=sQRTmNxVEpSmAvM6PUgJkScKMe2iMHS0g/6yQAy4zTQFeSHQFyuoH2SBf4x3Eb7/bh/XJKgwUVFHqDgF63bTcQmZI2p9u2Dg0VxhZmKbIg1cnVSz0PSWTlcbtfno; AWSALBCORS=sQRTmNxVEpSmAvM6PUgJkScKMe2iMHS0g/6yQAy4zTQFeSHQFyuoH2SBf4x3Eb7/bh/XJKgwUVFHqDgF63bTcQmZI2p9u2Dg0VxhZmKbIg1cnVSz0PSWTlcbtfno; _uetsid=e8de7d80dfbc11eebc0de5b8e48b98ad; _uetvid=73cb17c0cda711ee8c4ee73a7e464ae2; _clsk=1os1mgd%7C1710183917239%7C5%7C0%7Co.clarity.ms%2Fcollect',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        "user-agent": random_user_agent
    }
    
    return headers

async def GetRandomProxy(): # Get all working proxies from the working_proxies.txt file
    with open('working_proxies.txt', 'r') as f:
        proxy = f.read().splitlines()
    return random.choice(proxy)

async def GetRandomQueuedProxy(): # Retrieves a random proxies from queued_proxies.txt file; Helper for TestProxies() function
    with open('queued_proxies.txt', 'r') as f:
        proxy = f.read().splitlines()
    return random.choice(proxy)

async def WriteProxy(proxy): # Writes a working proxy to the working_proxies.txt file
    with open('working_proxies.txt', 'a') as f:
        f.write(proxy + '\n')

async def RemoveProxy(proxy): # Removes a non-working proxy from queued_proxies txt file
    with open('queued_proxies.txt', 'r') as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines if line.strip() != proxy]

        with open('queued_proxies.txt', 'w') as f:
            f.write('\n'.join(lines)) 

async def RotateUserAgent(): # Rotates through User Agents by swapping proxies and headers; Returns a working proxy and random header
    
    headers = await RotateHeaders() # Retrieve a random header
    proxy = await GetRandomProxy() # Retrieve a working proxy

    return proxy, headers

async def TestProxies(URL_LINK): #Queues up proxy to be used in main() function. Runs along side main()
    while True:
        proxy = await GetRandomQueuedProxy()
        proxy_URL = f'socks5://{proxy}'

        try:
            async with httpx.AsyncClient(proxies = {"http://": proxy_URL, "https://": proxy_URL}) as client:
                r = await client.get(URL_LINK)
                if r.status_code in (200, 403):
                    await WriteProxy(proxy)
                    print(f'Proxy Works: {proxy} - Status: {r.status_code}')

        except Exception as e:
            print(f'Proxy: {proxy} failed! Status: {e}\n Retrying with new proxy...')
            await RemoveProxy(proxy) # Remove proxy from queued_proxies text file    

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

        if "blocked" in await url.content() or url.status == 403: # Necessary Redundant Clause; Sometimes page still loads just to output an Error 403 page which we do not want.
            print("Blocked by Zillow. Trying again with new headers...")
            headers_new, proxy_new = await RotateUserAgent()
            await browser.close()
            await main(URL_LINK, proxy_new, headers_new)
            return
        else:
            print("Success accessing the URL.")
        
        # ***SCRAPING TASKS HERE***
            
        # CAPTCHA CHECK HERE; hold the button for x seconds, if page doesn't update, refresh and try again, if page closes, reopen and try again 
        # If page randomly closes, reopen and try again
        # Refresh Page
        # Hold Button down for x seconds
        # If page doesn't update, refresh and try to hold down button again
        # if CAPTCHA is successful, move to next step

    except Exception as e:
        if "Page' object has no attribute 'status'" in str(e): # Flag when we run off our Address; Really just a testing clause
            print("The exception 'Page' object has no attribute 'status' occurred. Continuing without closing the browser.")
        else:
            print(f'Error in main(): {e}')
            proxy_new, headers_new = await RotateUserAgent() # Retry the process with a new user agent
            await browser.close()
            print("Retrying with new Proxy and Headers")
            await main(URL_LINK, proxy_new, headers_new)
            return
            
    finally:        
        await asyncio.sleep(random.randint(50,100)) # Random sleep time to avoid detection; long for testing
        await browser.close()    

async def MainWrapper():
    URL_LINK = 'https://www.zillow.com/homedetails/705-Puesta-Del-Sol-Plz-Indialantic-FL-32903/43474044_zpid/' # Once functions are created, this will link to whatever specific Zillow webpage we want to scrape
    proxy, headers = await RotateUserAgent()
    await asyncio.gather(main(URL_LINK, proxy, headers), TestProxies(URL_LINK))
            
asyncio.run(MainWrapper())