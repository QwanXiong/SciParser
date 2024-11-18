import requests
import json
from sentence_transformers import SentenceTransformer
#from bs4 import BeautifulSoup as bs
#from selenium import webdriver
#from selenium.webdriver.common.by import By
import time
#import re


model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def vecs(text,model):
    #print(model)
    
    text=model.encode([text])[0]
    return text

#def tandof_abst(url):
#    
#    driver = webdriver.Chrome()
#    driver.set_page_load_timeout(5)
#    #wait =
#    
#    try:
#        driver.get(url)
#        html_source=driver.page_source
#
#    except:
#        driver.execute_script("window.stop();")
#        html_source=driver.page_source
#
#
#    
#
#    tree=bs(html_source,'html.parser')
#    try:
#        return(tree.find('div',{'class':'hlFld-Abstract'}).p.text)
#    except:
#        return('None')
#
#def tandof_abst_gs(doi):
#    with requests.Session() as s:
#        doi =doi.replace('/','%2F')
#        #https://serpapi.com/search.json?engine=google_scholar&q=biology
#
#        #URL = 'https://scholar.google.com/scholar?hl=ru&as_sdt=0%2C5&q='+doi+'+&btnG='
#        #URL = "https://serpapi.com/search.json?engine=google_scholar&q="+doi
#        #search_query = scholarly.search_pubs(doi)
#        #print(scholarly.pprint(next(search_query)))
#        '''params = {'asynchronous':True, 
#         'evalScripts':True, 
#         'method':'get'
#        }
#        headers =  {
#                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#                "Accept-Encoding":"gzip, deflate, br, zstd",
#                "Accept-Language":"en-US,en;q=0.5",
#                "Connection":"keep-alive",
#                "Host": "scholar.google.com",
#                "Priority": "u=0, i",
#                "Referer": URL,
#                "Sec-Fetch-Dest": "document",
#                "Sec-Fetch-Mode":"navigate",
#                "Sec-Fetch-Site":"same-origin",
#                "Upgrade-Insecure-Requests": "1",
#                "User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0"
#            }
#        resp=s.get(URL)
#        print(resp.content,resp)
#        print(URL)
#        fil=open('text.txt','w')
#        res = re.search(r'<div class="gsh_csp">(.*?)</div>',resp.content.decode())
#        fil.write(resp.content.decode())
#        fil.close()'''
#        assert False
#        #print(type(str(resp.content)),str(resp.content))
#        if res is not None:
#            #print(
#            return(res.group(1))
#        else:
#            return 'None'
#


def crossref_api(issn,date,offset):
    
    assert offset%100==0
    url="http://api.crossref.org/journals"+"/"+issn+"/works?filter=from-index-date:"+date+'&rows=100'+'&offset='+str(offset)
    try:
        tree=requests.get(url)
    except:
        time.sleep(3)
        tree=requests.get(url)
     
    js_obj=json.loads(tree.content)
    if len(js_obj['message']['items'])==0:
        return {}
    dic={'issue':[],'doi':[],'type':[],'title':[],'author':[],'volume':[],'abstract_vec':[],'abstract':[]}
    for i in js_obj['message']['items']:
        #print('sdf')
        if 'abstract' not in i.keys():#for future: if no abstract add title of the article
#            if i['publisher']=='Informa UK Limited':
#                
#                abstract_tand=tandof_abst('https://www.tandfonline.com/doi/full/'+i['DOI'])
#                
#                if abstract_tand=='None':
#                     dic['abstract'].append(i['title'])
#                     dic['abstract_vec'].append(vecs(i['title'][0],model))
#                else:               
#                    dic['abstract'].append(abstract_tand)
#                    dic['abstract_vec'].append(vecs(abstract_tand,model))
#
#                
#            else:
            dic['abstract'].append(i['title'])
            dic['abstract_vec'].append(vecs(i['title'][0],model))
        else:
            dic['abstract_vec'].append(vecs(i['abstract'],model))
            dic['abstract'].append(i['abstract'])
        if 'issue' in i.keys():
            dic['issue'].append(i['issue'])
        else:
            dic['issue'].append('')
        if 'volume' in i.keys():
            dic['volume'].append(i['volume'])
        else:
            dic['volume'].append('')
        dic['doi'].append(i['DOI'])
        dic['type'].append(i['type'])
        dic['title'].append(i['title'][0])
         
        
        author=[]
        if "author" in i.keys():
            for d in i['author']:
                if 'given' not in d.keys():
                   # print(d,i['DOI'])
                    if 'family' not in d.keys():
                        #print(d,i['DOI'])
                        author.append(' ')
                    else:
                        author.append(d['family'])
                else:
                    author.append(' '.join([d['given'],d['family']]))
        else:
            author.append(' ')
        
        #au
        
        dic['author'].append(', '.join(author))
    return dic
