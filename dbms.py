import sqlite3
from crossref_api import crossref_api,vecs
import pandas as pd
import numpy as np
import os
from scipy.spatial import distance
from sentence_transformers import SentenceTransformer

model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
class database:
    def __init__(self):
        print('DATABASE CLASS INITIALIZED')
        self.con=sqlite3.connect('database.db')
        self.cur=self.con.cursor()
        self.queue=self.queue(self.cur)
        self.journals=self.journals(self.cur)
        self.papers=self.papers(self.cur)
        self.users=self.users(self.cur)

    def comm(self):
        self.con.commit()

    def close_con(self):
        self.con.close()
    
    class queue:
        def __init__(self,cursor):
            self.cur=cursor
        def create_table(self):
            self.cur.execute('''CREATE TABLE IF NOT EXISTS queue
                            (paper_id INTEGER,
                            area_id INTEGER,
                            user_id INTEGER)             
                            ''')
        def papers_search(self,last_papers=None,user_id='all'):

            #self.cur.
            
            if last_papers==None:
                self.cur.execute('SELECT paper_id,abstract_vec,journal_id FROM papers')
                papers_arr=self.cur.fetchall()
            else:
                papers_arr=last_papers
            self.cur.execute('SELECT area_id, keywords_vec FROM keywords')
            keywords_arr=self.cur.fetchall()
            sqtup=[]
            for i in keywords_arr:
                if user_id!='all':
                    self.cur.execute('SELECT * FROM users_to_keywords WHERE user_id=? AND area_id=?',(user_id,i[0]))
                   # u_id=self.cur.fetchall()
                    #print(u_id)
                    if len(self.cur.fetchall())==0:
                        continue
                
                
                for d in papers_arr:
                    #print(i[1].replace('\n',' ').replace('[','').replace(']',''),'|||||')#,np.fromstring(i[1].replace('\n','')),np.fromstring(i[1]).shape)
                    #print(np.fromstring(i[1].replace('\n','').replace('[','').replace(']',''),sep='  '),np.fromstring(i[1].replace('\n',' ').replace('[','').replace(']',''),sep='  ').shape)
                    dist_=(1-distance.cosine(np.fromstring(i[1].replace('\n','').replace('[','').replace(']',''),sep='  '),np.fromstring(d[1].replace('\n','').replace('[','').replace(']',''),sep='  ')))
                    if dist_>0.3:
                        #print(i[0])
                        #if d[2]
                       # if user_id='all':
                        self.cur.execute('SELECT user_id FROM users_to_keywords WHERE area_id==?',(i[0],))
                        
                        user_id=self.cur.fetchone()[0]
                        #print((user_id,int.from_bytes(d[2],'little')))
                        self.cur.execute('SELECT * FROM users_to_journals WHERE user_id=? AND journal_id=?',(user_id,int.from_bytes(d[2],'little')))
                        u_t_j=self.cur.fetchall()
                        #print(u_t_j)
                        if len(u_t_j) !=0:
                            sqtup.append((d[0],i[0],user_id))
            for i in sqtup:
                self.cur.execute('INSERT INTO queue VALUES (?,?,?)',i)
                    
        def send_user_papers(self,user_id):
            self.cur.execute('SELECT * FROM queue WHERE user_id=?',(user_id,))
            queue_table=self.cur.fetchall()
            dic={'paper_id':[],'title':[],'abstract':[],'journal':[],'area':[],'doi':[]}
            for i in queue_table:
                self.cur.execute('SELECT paper_id,title,abstract,journal_id,doi FROM papers WHERE paper_id=?',(i[0],))
                paper=self.cur.fetchone()
                dic['paper_id'].append(paper[0])
                dic['title'].append(paper[1])
                dic['abstract'].append(paper[2])
                dic['doi'].append(paper[4])
                #print(paper[3])
                self.cur.execute('SELECT area_name FROM keywords WHERE area_id=?', (i[1],))
                area=self.cur.fetchone()
                dic['area'].append(area[0])
                self.cur.execute('SELECT journal_name FROM journals WHERE journal_id=?',(int.from_bytes(paper[3],'little'),))
                journal=self.cur.fetchone()
                dic['journal'].append(journal[0])
            self.cur.execute('DELETE FROM queue WHERE user_id=?',(user_id,))
            return dic



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
            
            #print(id_)
            self.cur.execute('SELECT issn FROM journals WHERE issn=?',(issn,))
            issn_=self.cur.fetchall()
            #print(issn_,len(issn_))
            if len(issn_)==0:
                self.cur.execute('INSERT INTO journals VALUES (?,?,?)',(id_,name,issn))
                
        def show(self):
            self.cur.execute('''SELECT * FROM journals''')
            journ=self.cur.fetchall()
            
            dic={'journal_id':[],'journal_name':[],'issn':[]}
            for i in journ:
                dic['journal_id'].append(i[0])
                dic['journal_name'].append(i[1])
                dic['issn'].append(i[2])
            return dic
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
                             journal_id INT)''')

                   
        def update(self,date):
            
            self.cur.execute('SELECT journal_id,issn FROM journals')
            
            jour=self.cur.fetchall()
            last_papers=[]
            for i in jour:
                print('journal: ',i)
                d=0
                data=pd.DataFrame()
                a=0
                while a!={}:
                    a=crossref_api(i[1],date,d)
                    
                    data=pd.concat([data,pd.DataFrame(a)],ignore_index=True)
                    d+=100
                    #break
                    #if d%500==0:
                        #print('d=')
                #print('hihi',type(i[0]))    
                data['journal_id']=[int(i[0]) for c in range(data.shape[0])]
                
                
                self.cur.execute('SELECT MAX(paper_id) FROM papers')
                ids=self.cur.fetchone()
                if not ids[0]==None:
                    id_=ids[0]+1
                else:
                    id_=1
                
                for d in range(data.shape[0]):
                   
                    #print( data['title'][d])
                    #print(data['journal_id'][d])
                    self.cur.execute('SELECT doi FROM papers WHERE doi=?',(data['doi'][d],))
                    doi=self.cur.fetchall()
                    if len(doi)==0:
                        self.cur.execute('INSERT INTO papers VALUES(?,?,?,?,?,?,?,?,?,?)',(id_,data['title'][d],data['type'][d],data['author'][d],data['volume'][d],data['issue'][d],str(data['abstract'][d]),str(data['abstract_vec'][d]),data['doi'][d],data['journal_id'][d]))
                        last_papers.append((id_,str(data['abstract_vec'][d]),data['journal_id'][d]))
                        id_+=1
            print('updated journals')
            #self.cur.execute("SELECT journal_id FROM papers")
            #print(self.cur.fetchall())
            
            database.queue(self.cur).papers_search(last_papers=last_papers)
    class users:

        def __init__(self,cursor):
            self.cur=cursor
      
        def create_table(self):
            self.cur.execute('''CREATE TABLE IF NOT EXISTS users
                            (telegram_chat_id INTEGER PRIMARY KEY,
                            telegram_user_name TEXT NOT NULL,
                            telegram_name TEXT NOT NULL,
                            update_period INTEGER,
                            last_update_time TEXT)''')
            self.cur.execute('''CREATE TABLE IF NOT EXISTS keywords
                            (area_id INTEGER PRIMARY KEY,
                            area_name TEXT NOT NULL,
                            keywords TEXT NOT NULL,
                            keywords_vec TEXT NOT NULL)''')
            self.cur.execute('''CREATE TABLE IF NOT EXISTS users_to_keywords
                            (user_id INTEGER,
                            area_id INTEGER)''')
            self.cur.execute('''CREATE TABLE IF NOT EXISTS users_to_journals
                            (user_id INTEGER,
                            journal_id INTEGER)''')
            

        def show_con_jour(self):
            self.cur.execute('SELECT * FROM users_to_journals')
            u_t_j = self.cur.fetchall()
            #print(u_t_j)
            return (u_t_j)
            #TODO: transform to dict in a proper way
            

        def add(self,telegram_id,telegram_user_name,telegram_name,update_period,last_update_time):
           
            try:
                #print(
                self.cur.execute('INSERT INTO users VALUES (?,?,?,?,?)',(telegram_id,telegram_user_name,telegram_name,update_period,last_update_time))
            except:
                print('error adding a user')

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
        
        def add_con_jour(self,user_id,issn_):
            self.cur.execute('SELECT journal_id FROM journals WHERE issn=?',(issn_,))
            jour_id=self.cur.fetchone()[0]
            #print(issn_,jour_id)
            self.cur.execute('INSERT INTO users_to_journals VALUES (?,?)',(user_id,jour_id))
        def show(self):
            self.cur.execute('''SELECT * FROM users''')
            user=self.cur.fetchall()
            
            dic={'telegram_chat_id':[],'telegram_user_name':[],'telegram_name':[],'update_period':[],'last_update_time':[]}
            for i in user:
                dic['telegram_chat_id'].append(i[0])
                dic['telegram_user_name'].append(i[1])
                dic['telegram_name'].append(i[2])
                dic['update_period'].append(i[3])
                dic['last_update_time'].append(i[4])
                
            return dic

        def show_keywords(self):
            self.cur.execute('SELECT * FROM keywords')
            keywords=self.cur.fetchall()
            
            #print('keywords: ',keywords) 
            dic={'user_id':[],'area':[],'keywords':[]}
            for i in keywords:
                dic['area'].append(i[1])
                dic['keywords'].append(i[2])
                self.cur.execute('SELECT user_id FROM users_to_keywords WHERE area_id=?',(i[0],))
                u_t_k=self.cur.fetchone()
                dic['user_id'].append(u_t_k[0])
            return dic

database_instance = database()
      
      
#print('asdsad'
'''
connection=sqlite3.connect('database.db')
cursor=connection.cursor()
j=journals(cursor)
j.create_table()
j.add('International Organization','0020-8183')
j.add('American Political Science Review','0003-0554')
u=users(cursor)
u.create_table()
u.add(123,'MArco123','Marc Ivanovicj',30,'2024-01-01')
u.add_keywords(123,'climate change','climate, global warming, heatwaves, cold snaps, forest fires')
u.add_con_jour(123,1)
p=papers(cursor)
p.create_table()
print('created_tables')
cursor.execute('SELECT * FROM journals')
print(cursor.fetchall())

queue(cursor).create_table()
p.update('2024-01-01')
print('created_queue')




cursor.execute('SELECT * FROM queue')
qu=cursor.fetchall()
for i in qu:
    
    aa=cursor.execute('SELECT title,abstract,journal_id FROM papers WHERE paper_id=?',(i[0],))
    aa=cursor.fetchall()
    print(aa)
    print(int.from_bytes(aa[0][2],'little'))
    cursor.execute('SELECT journal_name FROM journals WHERE journal_id=?',(int.from_bytes(aa[0][2],'little'),))
    print(cursor.fetchall())
    print('____')
connection.commit()
connection.close()
#fil=open('test_text.txt','w',encoding='utf-16le')
#print(cursor.fetchone())
#fil.write(str(cursor.fetchall()))
#fil.close()
'''
'''
db=database()
db.users.add(123,'mama','sadsa',30,'2024-01-01')
db.users.add_keywords(123,'climate','climate change climate politics international climate regime environmental law')
db.users.add_con_jour(123,'0003-0554')
db.papers.update('2024-10-01')
print(db.queue.send_user_papers(123))
db.users.add(432,'asdasd','fff',30,'2024-01-01')
db.users.add_keywords(432,'physics','molecular dynamics quantum world chemical physics')
db.users.add_con_jour(432,'0022-4073')
db.users.add_con_jour(432,'1463-9084')
db.queue.papers_search(user_id=432)
#print(db.queue.send_user_papers(432))
print('_____')
print(db.cur.execute("SELECT * FROM queue").fetchall())
#print(db.queue.send_user_papers(123))
          
              
'''
