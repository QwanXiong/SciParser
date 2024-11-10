import requests
import json
from scipy.spatial import distance
from sentence_transformers import SentenceTransformer
import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def vecs(text,model):
    #print(model)
    text=model.encode([text])[0]
    return text

def tandof_abst(url):
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(5)
    #wait =
    
    try:
        driver.get(url)
        html_source=driver.page_source

    except:
        driver.execute_script("window.stop();")
        html_source=driver.page_source


    

    tree=bs(html_source,'html.parser')
    try:
        return(tree.find('div',{'class':'hlFld-Abstract'}).p.text)
    except:
        return('None')
    

def crossref_api(issn,date,offset):
    #if offset%100!=0:
    assert offset%100==0
    url="http://api.crossref.org/journals"+"/"+issn+"/works?filter=from-pub-date:"+date+'&rows=100'+'&offset='+str(offset)
    tree=requests.get(url)
     
    js_obj=json.loads(tree.content)
    if len(js_obj['message']['items'])==0:
        return {}
    dic={'issue':[],'doi':[],'type':[],'title':[],'author':[],'volume':[],'abstract_vec':[],'abstract':[]}
    for i in js_obj['message']['items']:
        #print(i)
        if 'abstract' not in i.keys():#for future: if no abstract add title of the article
            if i['publisher']=='Informa UK Limited':
                
                abstract_tand=tandof_abst('https://www.tandfonline.com/doi/full/'+i['DOI'])
                if abstract_tand=='None':
                     dic['abstract'].append(i['title'])
                     dic['abstract_vec'].append(vecs(i['title'][0],model))
                else:               
                    dic['abstract'].append(abstract_tand)
                    dic['abstract_vec'].append(vecs(abstract_tand,model))

                
            else:
                continue
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
        dic['title'].append(i['title'])
         
        
        author=[]
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
        
        #au
        
        dic['author'].append(', '.join(author))
    return dic
    
data=pd.DataFrame()
for i in range(0,100,100):
    print(i)
    #a=crossref_api('0021-9606','2024-01-01',i) #journal of chemcial physics
    a=crossref_api('2154-8978','2024-01-01',i) #polar journal (no abstracts in crossref)
    #a=crossref_api('0003-0554','2024-01-01',i) #American Political Science Review
   # a=crossref_api('0144-235X','2024-01-01',i) #International review of physical chemistry
    data=pd.concat([data,pd.DataFrame(a)])

    if a=={}:
        break
#print(data)
#keywords='Molecular dynamics computational chemistry atomic simulations statistical mechanics statistical physics'
keywords='International regimes governance international organiation interstate relations international politics cooperation'
keywords=vecs(keywords,model)
#print(keywords.shape)
#print(model)
dist=[]
for i in range(data.shape[0]):
    #print(i,data['abstract_vec'].tolist()[i].shape,keywords.shape)
    
    dist.append(1-distance.cosine(data['abstract_vec'].tolist()[i],keywords))
data['dist']=dist
print(data.sort_values(by='dist',ascending=False)['title'].head(10).tolist())
print(data.sort_values(by='dist',ascending=False)['title'].tail(10).tolist())
