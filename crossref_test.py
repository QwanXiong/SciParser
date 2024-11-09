import requests
import json
from scipy.spatial import distance
from sentence_transformers import SentenceTransformer
import pandas as pd

model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def vecs(text,model):
    #print(model)
    text=model.encode([text])[0]
    return text

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
            continue
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
         
        dic['abstract_vec'].append(vecs(i['abstract'],model))
        dic['abstract'].append(i['abstract'])
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
for i in range(0,200,100):
    print(i)
    #a=crossref_api('0021-9606','2024-01-01',i) #journal of chemcial physics
    #a=crossref_api('2154-8978','2024-01-01',i) #polar journal (no abstracts in crossref)
    a=crossref_api('0003-0554','2024-01-01',i) #American Political Science Review
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
print(data.sort_values(by='dist',ascending=False)['abstract'].head(10).tolist())
print(data.sort_values(by='dist',ascending=False)['abstract'].tail(10).tolist())
