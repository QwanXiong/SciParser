
import requests
import json
import re
import time
import pickle





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
        #URL = 'https://scholar.google.com/'
        #URL = 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=article&btnG='
        params = {'asynchronous':True, 
         'evalScripts':True, 
         'method':'get'
        }
        headers =  {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate, br, zstd",
            "Accept-Language":"en-US,en;q=0.5",
            "Connection":"keep-alive",
            #"Cookie": u"NID=519=RyuVY4iR7oJA14GSrCKsRoHxXUdqY63uZs6k1wL-kQMcZ3elX3ToQ28OyLM3ShifKbfUYjm1uscmeLYfyrtR-TMIT9mZh1D3tdF5s6L-htW7LZAs0yNJwFpyqCM895XFzZn8SGbzZY6z9AYmuPDQCh50274wAbYp4j5ZTXkLyNRFLq66vprzx8O3ihmmUp157plh_p2sHBw4z9MB63uiwUZ71y9fysHFabEgqwJt-C-fuc042WgIfE37tXzNOxAUlWzSnZGNibawpoumlX-Ll_PBCRKCshpnHwZf6D8rqVzZ6bR4O3UqnUBS3Nb-PEc7Z_Cc7YWl2aMFN14rbNWagIh_QdhIoaOVzguPgTraMekrfS__jtTiehse3EkbnAg0zS_jsqHr2x7b5v_X1I9Ept0v5p2NRM9jCpLdch8IbqUMFV2STl4rH-GMiocAhdQhlJRvz448cAgBlG2p-YQSeBeA; GSP=LM=1716448887:S=KClEgH2GiHUZfdW4pL9wkqEWByatqkQWlaDzdKvVCcOKxYxvj7lxJwk6UCBAA; __Secure-ENID=21.SE=EnZ5JaAXEOGa96irfspCBbsr7mu0yxmiH73q-36u_3eA62mekaxGqxwd1fsUF077pGmCrnRHvyDJGduhr3ILxajTfhXCIFD8vxcp7BLzeMf4CPAn4-431654Uo0G5MkayXlp2szp47RyM3j-YVJacwCHquMHiP_y8OjT2Nm7nLNSTcsUnwc1n0JrcqSBoIbeLhyUvM_a3dMiergTdYK3R68QtFDNMiZF0uvp9AKwES5vXJtpHpi3oaHYI5c0fjA-M5D3LQBnQnOOgFQlhbnPz88so-Qdo6qfupaE_1hicOqD_Q0BBE7fM8Uc4vlIt0ZwXM1NdM1TfpT_N4f280j_UaVUxsnrsgo-QX6U-E-B4AkcpjxY5XOy_g; AEC=AZ6Zc-W0qHg0q9DqfAfY4DdP-GQqi8I0zrqeHoqzA6LqfiGtlnsUnTAfPQ",
            "Host": "scholar.google.com",
            "Priority": "u=0, i",
            #"Referer": "https://scholar.google.com/scholar?hl=ru&as_sdt=0%2C5&q=https%3A%2F%2Fdoi.org%2F10.1080%2F2154896X.2024.2342109+&btnG=",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode":"navigate",
            "Sec-Fetch-Site":"none",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0"
        }
        #headers ={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
        #    }
       # cookies = {'GSP': 'LM=1731240616:S=5umxnT-vRFItU3uK'}
       # cookies = {'NID': '519=dppCxVaiuZFvi5oCBxVSqkZyQp_Y3cSDMakFVTpNNb6f1WY1-DOZ90El5WNdoqp91Qe26nM2bYKMhTMJ4l0AV6GsAPu0Rfl7cmgqskQr9k6gxHXqKxNd64AWgvZN9Rtb1VdeUl-uLl4Rov_cDXUix2QUK8Kw3Ymb4seI2lPqcQP482kZjFE', 
       #            'GSP': 'LM=1731316286:S=gEX83XKsGq9vuCBQ'}


        #with open('cookiefile', 'rb') as f:
        #    s.cookies.update(pickle.load(f))
        for i in range(1000):
            resp = s.get(URL,headers=headers,params=params)
            #resp = requests.get(URL)
            print(i,resp)
            #print(resp.text)
            res = re.search(r'<div class="gsh_csp">(.*?)</div>',resp.text)
            if res is not None:
                print(res.group(1))

           # print(resp.cookies.get_dict())
            print(s.cookies.get_dict())
           # resp = s.get(URL,headers=headers)
           # print(resp.cookies.get_dict())
           # print(s.cookies.get_dict())
        #with open('cookiefile', 'wb') as f:
        #    pickle.dump(s.cookies, f)
      #  res = re.search(r'<div class="gsh_csp">(.*?)</div>',resp.content.decode('utf-8'))
      #  if res is not None:
      #      print(res.group(1))



if __name__ == '__main__':
    get_request()

