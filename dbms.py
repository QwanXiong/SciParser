import sqlite3
from crossref_api import crossref_api,vecs
import pandas as pd
import numpy as np
import os
from scipy.spatial import distance
from sentence_transformers import SentenceTransformer

model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

class queue:
    def __init__(self,cursor):
        self.cur=cursor
    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS queue
                        (paper_id INTEGER PRIMARY KEY,
                        area_id INTEGER,
                        user_id INTEGER)             
                        ''')
    def papers_search(self):
        self.cur.execute('SELECT paper_id,abstract_vec FROM papers')
        papers_arr=self.cur.fetchall()
        self.cur.execute('SELECT area_id, keywords_vec FROM keywords')
        keywords_arr=self.cur.fetchall()
        sqtup=[]
        for i in keywords_arr:
            dist_list=[]
            for d in papers_arr:
                #print(i[1].replace('\n',' ').replace('[','').replace(']',''),'|||||')#,np.fromstring(i[1].replace('\n','')),np.fromstring(i[1]).shape)
                #print(np.fromstring(i[1].replace('\n','').replace('[','').replace(']',''),sep='  '),np.fromstring(i[1].replace('\n',' ').replace('[','').replace(']',''),sep='  ').shape)
                dist_list.append(1-distance.cosine(np.fromstring(i[1].replace('\n','').replace('[','').replace(']',''),sep='  '),np.fromstring(d[1].replace('\n','').replace('[','').replace(']',''),sep='  ')))
            for d in range(len(dist_list)):
                if dist_list[d]>0.3:
                    #print(i[0])
                    self.cur.execute('SELECT user_id FROM users_to_keywords WHERE area_id==?',(i[0],))
                    user_id=self.cur.fetchone()[0]
                    sqtup.append((papers_arr[d][0],i[0],user_id))
        for i in sqtup:
            self.cur.execute('INSERT INTO queue VALUES (?,?,?)',i)
                
        



class journals:
    def __init__(self,cursor):
        self.cur=cursor

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS journals
                        (journal_id INTEGER PRIMARY KEY,
                         journal_name TEXT NOT NULL,
                         issn TEXT NOT NULL)''')
        
    
    def add(self,name,issn):
        self.cur.execute('SELECT MAX(journal_id) FROM journals')
        ids=self.cur.fetchone()
        #print(ids)
        if not ids[0]==None:
            id_=ids[0]+1
        else:
            id_=1
        
            
        self.cur.execute('INSERT INTO journals VALUES (?,?,?)',(id_,name,issn))
class papers:
    def __init__(self,cursor):
        self.cur=cursor
    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS papers
                        (paper_id INTEGER PRIMARY KEY,
                         title TEXT NOT NULL,
                         type TEXT NOT NULL,
                         author TEXT NOT NULL,
                         volume TEXT NOT NULL,
                         issue TEXT NOT NULL,
                         abstract TEXT NOT NULL,
                         abstract_vec TEXT NOT NULL,
                         doi TEXT NOT NULL,
                         journal_id INTEGER)''')

               
    def update(self,date):
        self.cur.execute('SELECT journal_id,issn FROM journals')
        
        jour=self.cur.fetchall()
        
        for i in jour:
            d=0
            data=pd.DataFrame()
            a=0
            while a!={}:
                a=crossref_api(i[1],date,d)
                
                data=pd.concat([data,pd.DataFrame(a)])
                d+=100
                #break
            data['journal_id']=[i[0] for c in range(data.shape[0])]
            
            
            self.cur.execute('SELECT MAX(paper_id) FROM papers')
            ids=self.cur.fetchone()
            if not ids[0]==None:
                id_=ids[0]+1
            else:
                id_=1
            for d in range(data.shape[0]):
               
                
                self.cur.execute('INSERT INTO papers VALUES(?,?,?,?,?,?,?,?,?,?)',(id_,data['title'][d],data['type'][d],data['author'][d],data['volume'][d],data['issue'][d],str(data['abstract'][d]),str(data['abstract_vec'][d]),data['doi'][d],data['journal_id'][d]))
                id_+=1
        print('updated journals')   
        queue(self.cur).papers_search()
class users:
    def __init__(self,cursor):
        self.cur=cursor
    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users
                        (telegram_chat_id INTEGER PRIMARY KEY,
                        telegram_user_name TEXT NOT NULL,
                        telegram_name TEXT NOT NULL,
                        update_period INTEGER,
                        last_update_time DATE)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS keywords
                        (area_id INTEGER PRIMARY KEY,
                        area_name TEXT NOT NULL,
                        keywords TEXT NOT NULL,
                        keywords_vec TEXT NOT NULL)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users_to_keywords
                        (user_id INTEGER,
                        area_id INTEGER)''')

    def add(self,telegram_user_name,telegram_name,update_period,last_update_time):
        self.cur.execute('SELECT MAX(telegram_chat_id) FROM users')
        ids=self.cur.fetchone()
        #print(ids)
        if not ids[0]==None:
            id_=ids[0]+1
        else:
            id_=1
        
            
        self.cur.execute('INSERT INTO users VALUES (?,?,?,?,?)',(id_,telegram_user_name,telegram_name,update_period,last_update_time))

    def add_keywords(self,user_id,area,keywords):
        self.cur.execute('SELECT MAX(area_id) FROM keywords')
        ids=self.cur.fetchone()
        #print(ids)
        if not ids[0]==None:
            id_=ids[0]+1
        else:
            id_=1
        #print(type(vecs(keywords,model)),vecs(keywords,model).shape)
        self.cur.execute('INSERT INTO keywords VALUES (?,?,?,?)',(id_,area,keywords,str(vecs(keywords,model))))
        self.cur.execute('INSERT INTO users_to_keywords VALUES (?,?)',(user_id,id_))
                            


      
      
#print('asdsad')
connection=sqlite3.connect('database.db')
cursor=connection.cursor()
j=journals(cursor)
j.create_table()
j.add('Journal of chemcial physics','0021-9606')
j.add('Sustainability','2071-1050')
u=users(cursor)
u.create_table()
u.add('MArco123','Marc Ivanovicj',30,'2024-01-01')
u.add_keywords(1,'climate change','climate, global warming, heatwaves, cold snaps, forest fires')
p=papers(cursor)
p.create_table()
print('created_tables')

queue(cursor).create_table()
p.update('2024-01-01')
print('created_queue')

cursor.execute('SELECT * FROM queue')
qu=cursor.fetchall()
for i in qu:
    
    cursor.execute('SELECT title,abstract FROM papers WHERE paper_id=?',(i[0],))
    print(cursor.fetchall())
    print('____')
connection.commit()
connection.close()
#fil=open('test_text.txt','w',encoding='utf-16le')
#print(cursor.fetchone())
#fil.write(str(cursor.fetchall()))
#fil.close()

              
              
