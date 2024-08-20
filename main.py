import requests
import json
import re
import time


def parse_issue_link(text):
    #print(text.split('\n'))
    res = re.search(r'href="(\S*)" class="button">View This Issue',text)
    print(res.group(1))
    #for lin in text:
    #    print(lin)
        #break
    link = None
    if res is not None:
        link = 'https://pubs.aip.org'+res.group(1)

    return link

def parse_article_names(text):
    #res = re.search(r'data-resource-id-access')
    spl = text.split('\n')
    #for i in range(10):
    #    print(spl[i])
    next_name = False
    names = []
    for lin in spl:
        res = re.search(r'data-resource-id-access',lin)
        if res is not None:
            next_name = True
            print(lin)
        if next_name == True:
            res = re.search(r'href=\S*">(.*)</a>',lin)
            if res is not None:
                print(res.group(1))
                next_name = False
                names.append(res.group(1))
    with open('current-issue-names.txt', 'w') as fil:
        for name in names:
            fil.write(name+'\n')


with requests.Session() as s:
    #URL = 'https://pubs.aip.org/aip/jcp'
    URL = 'https://pubs.aip.org/aip/cpr'
    # headers = headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
    # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    # 'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    # 'Content-Type': 'application/json',
    # 'Host': 'pubs.aip.org',
    # 'DNT': '1',
    # 'Connection': 'keep-alive',
    # 'Sec-Fetch-Dest': 'document',
    # 'Sec-Fetch-Mode': 'navigate',
    # 'Sec-Fetch-Site': 'none'}
    headers ={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
        }
    resp = s.get(URL,headers=headers)
    #print(resp)
    issue_link = parse_issue_link(resp.text)
    print(issue_link)
    time.sleep(1)
    resp = s.get(issue_link,headers=headers)
    print(resp)
    parse_article_names(resp.text)
