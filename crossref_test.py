import requests
import json

def crossref_api(issn,date,offset):
    #if offset%100!=0:
    assert offset%100==0
    url="http://api.crossref.org/journals"+"/"+issn+"/works?filter=from-pub-date:"+date+'&rows=100'+'&offset='+str(offset)
    tree=requests.get(url)
     
    js_obj=json.loads(tree.content)
    if len(js_obj['message']['items'])==0:
        return {}
    dic={'issue':[],'doi':[],'type':[],'title':[],'author':[]}
    for i in js_obj['message']['items']:
        dic['issue'].append(i['issue'])
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

for i in range(0,10000,100):
    print(i)
    a=crossref_api('0021-9606','2024-01-01',i)
   

    if a=={}:
        break
