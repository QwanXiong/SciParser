
import requests
import json
import re
import time






def get_request():
    with requests.Session() as s:
       # URL = 'https://pubs.aip.org/aip/jcp'
        URL = 'https://www.tandfonline.com/doi/full/10.1080/2154896x.2024.2342109'
       # headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
       # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
       # 'Accept-Language': 'en-US,en;q=0.5',
       # 'Accept-Encoding': 'gzip, deflate, br, zstd',
       # 'Content-Type': 'application/json',
       # 'Host': 'www.tandfonline.com',
       # 'DNT': '1',
       # 'Connection': 'keep-alive',
       # 'Sec-Fetch-Dest': 'document',
       # 'Sec-Fetch-Mode': 'navigate',
       # 'Sec-Fetch-Site': 'none'}
        URL = 'https://scholar.google.com/scholar?hl=ru&as_sdt=0%2C5&q=10.1080%2F2154896X.2024.2342109+&btnG='
        params = {'asynchronous':True, 
         'evalScripts':True, 
         'method':'get'
        }
        headers =  {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate, br, zstd",
            "Accept-Language":"en-US,en;q=0.5",
            "Connection":"keep-alive",
            #"Cookie":"timezone=180; MAID=B/bFSLQ1YVJ4NE5/55o7hw==; MACHINE_LAST_SEEN=2024-11-10T00%3A21%3A09.017-08%3A00; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Apr+24+2024+10%3A42%3A35+GMT%2B0300+(Moscow+Standard+Time)&version=202402.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=472924bf-c65a-4666-be1a-78b05d9507bf&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&geolocation=RU%3BMOW&AwaitingReconsent=false; OptanonAlertBoxClosed=2024-04-24T07:42:35.647Z; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Nov+10+2024+11%3A21%3A11+GMT%2B0300+(Moscow+Standard+Time)&version=202409.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=472924bf-c65a-4666-be1a-78b05d9507bf&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&geolocation=RU%3BMOW&AwaitingReconsent=false; JSESSIONID=A299C81FF3D8EF850FCFAAEDD30B20EF; cf_clearance=p4cjqlfyl6rfPw2frHynYntwi_ZGba998xfgxzSL4A0-1731226870-1.2.1.1-raw.dXSa_axvrRqmuop75qx_6vBgjPW_hB7T7QHQdWkAL4QJzr3AXw7.1J5GK269O69fExa6_gVyZGsIREiv1JcSxaPb9BbKtZgnEsfhzNY_qMrEIQ6YBYsyvtBoKaHgQhQEtPzORGmQEJwWkutwM6Nf951NA6.9AoHCos8..0SFVxYQIy_XN_kCNq6eWDAEG_t2wSsKMqZW_BPOmJmx8mPR0cN1nkB5vnPb2EzpOHH_frE0xJ7qvpnnIx.D.IWtQS3ca4pkMY1O1f1wh3EvAk8PkUuk9aKRuETTrIQmHPixhQHUWmwGw8GHdZxlZBHseZHE66cfT28gUWrdS3WAQA",
            "Host": "scholar.google.com",
            "Priority": "u=0, i",
            "Referer": "https://scholar.google.com/scholar?hl=ru&as_sdt=0%2C5&q=https%3A%2F%2Fdoi.org%2F10.1080%2F2154896X.2024.2342109+&btnG=",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode":"navigate",
            "Sec-Fetch-Site":"same-origin",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0"
        }
        #headers ={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
        #    }
        resp = s.get(URL,headers=headers,params=params)
        #print(resp.content.decode())
        res = re.search(r'<div class="gsh_csp">(.*?)</div>',resp.content.decode())
        if res is not None:
            print(res.group(1))

    #    issue_link = parse_issue_link(resp.text)
    #    print(issue_link)
    #    time.sleep(1)
    #    resp = s.get(issue_link,headers=headers)
    #    print(resp)
    #    parse_article_names(resp.text)


if __name__ == '__main__':
    get_request()

