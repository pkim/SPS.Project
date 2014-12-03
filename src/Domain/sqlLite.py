#!/usr/bin/python

import sqlite3 
from macpath import curdir

class db():  
    def __init__(self, file):
        self.fileName = file

    def connect(self):
        self.conn = sqlite3.connect(self.fileName)
        self.cur = self.conn.cursor()

    def createTables(self):    
        self.cur.executescript("""   
            CREATE TABLE if not exists lecture (name varchar(100) primary key);
            
            CREATE TABLE if not exists document
            (
                docName varchar(100) primary key,
                path varchar(200),
                hash varchar(200),
                lecture_Name varchar(100),
                constraint lecture_Name foreign key (lecture_Name) references lecture(name)
                );
        """)

    def insert(self, dataset):
        #interate dictionary
        
        #values = dataset.
        self.cur.execute("INSERT INTO lecture VALUES(name);", "SEv14.5.SPS")
    
        
    def close(self):
        self.conn.commit()
        self.cur.close()

        
database = db("sqlLite.db")
database.connect()
database.createTables()

data = {"SEv14.5.SPS" : ["Python Basic", "/mnt/hgfs/FH/SPS/Workspace", "3253434" ]}

database.insert(data)




