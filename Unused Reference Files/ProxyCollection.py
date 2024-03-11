# Free Proxy sorting and validation; Sifts through a list of proxies (input) and writes working ones to output (working_proxies.txt)

import requests
import random
import itertools

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

def WriteProxy(proxy): # Writes a working proxy to the working_proxies.txt file

    with open('working_proxies.txt', 'a') as f:
        f.write(proxy + '\n')

def GetProxy(proxy): # Pulls a proxy from the input file
        with open('socks5.txt', 'r') as f:
            proxies = f.read().splitlines()
        return itertools.cycle(proxies)

def main():
    
    proxies = GetProxy('proxies.txt')
    for proxy in proxies:

        formattedProxySOCKS5 = {
            'http': f'socks5://{proxy}',
            'https': f'socks5://{proxy}'
        }
    
        formattedProxyHTTPS = {
            'http': f'http://{proxy}',
            'https': f'https://{proxy}'
        }

        try:
            response = requests.get('https://www.zillow.com', headers=RotateHeaders(), proxies=formattedProxySOCKS5, timeout=10)
            print(f'Proxy: {proxy} - Status: {response.status_code}')
            if response.status_code == 200 or response.status_code == 403: # 403 is a success code to get to the website, but is blocked since it's a bot
                print(f"Success with Proxy: {proxy}")
                WriteProxy(proxy)

        except Exception as e:
            print(f'Error w/ SOCKS5 Proxy {proxy}: {e}')
            continue # Comment out when ready to test HTTPS proxies
            try:
                response = requests.get('https://www.zillow.com', headers=RotateHeaders(), proxies=formattedProxyHTTPS)
                print(f'Proxy: {proxy} - Status: {response.status_code}')
                if response.status_code == 200:
                    WriteProxy(proxy)

            except:
                print(f'Error w/ HTTPS: {e}')
                continue       

main()             
            