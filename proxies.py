from lxml.html import fromstring
import requests
from itertools import cycle
import traceback

#https://api.proxyscrape.com/proxytable.php
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:20]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    response = requests.get('https://www.us-proxy.org/')
    parser = fromstring(response.text)
    for i in parser.xpath('//*[@id="proxylisttable"]/tbody/tr')[:20]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):        
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    response = requests.get('https://www.socks-proxy.net/')
    parser = fromstring(response.text)
    for i in parser.xpath('//*[@id="proxylisttable"]/tbody/tr')[:20]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):        
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


#proxies = ['121.129.127.209:80', '124.41.215.238:45169', '185.93.3.123:8080', '194.182.64.67:3128', '106.0.38.174:8080', '163.172.175.210:3128', '13.92.196.150:8080']
proxies = get_proxies()
print(proxies)
print(len(proxies))
"""
proxy_pool = cycle(proxies)

url = 'https://httpbin.org/ip'
for i in range(1,21):
    #Get a proxy from the pool
    proxy = next(proxy_pool)
    print("Request #%d"%i)
    print(proxy)
    try:
        response = requests.get(url,proxies={"http": proxy, "https": proxy})
        print("@@",response.json())
    except:
        print("Skipping. Connnection error")
"""