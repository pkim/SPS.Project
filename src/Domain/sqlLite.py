#!/usr/bin/python

import sqlite3 
from macpath import curdir

class db():  
    def __init__(self, file):
        self.fileName = file
        self.conn = sqlite3.connect(self.fileName)
        self.cur = self.conn.cursor()
        self.cur.executescript("""   
            CREATE TABLE if not exists lecture (name varchar(30) primary key);
            
            CREATE TABLE if not exists document
            (
                docName varchar(70) primary key,
                path varchar(200),
                hash varchar(50),
                lecture_Name varchar(30),
                constraint fk_lecture_Name foreign key (lecture_Name) references lecture(name)
                );
            
            CREATE TABLE if not exists version
            (
                docName varchar(70) primary key,
                ver decimal DEFAULT 0,
                constraint fk_docName foreign key (docName) references document(docName)
                );
        """)

    def insert(self, lectureName, courseDict):
        self.cur.execute('SELECT name FROM lecture WHERE name = :doc', {"doc":lectureName})
        row = self.cur.fetchone()
        if (row == None or row[0] != lectureName):
            self.cur.execute("INSERT INTO lecture VALUES (:name)", {"name" : lectureName})        
        
        for docName, list in courseDict.items():
            self.cur.execute("SELECT docName FROM document WHERE docName = :document", {"document":docName})
            row = self.cur.fetchone()
            if (row == None):
                print("Insert ", docName, list)
                self.cur.execute("INSERT INTO document VALUES(:docName, :path, :hash, :lecture_Name)", 
                                 {"docName" : docName, "path":list[0], "hash":list[1], "lecture_Name":lectureName}) 
                self.cur.execute("INSERT INTO version VALUES(:docName, :ver)", {"docName" : docName, "ver":1}) 
            else:
                print("Update ", docName, list)
                self.cur.execute("UPDATE document SET path = :path, hash = :newHash WHERE docName = :doc", 
                                 {"path" : list[0], "newHash":list[1], "doc" : docName})
                self.cur.execute('SELECT ver FROM version')
                row = self.cur.fetchone()
                newVer = row[0] + 1
                self.cur.execute("UPDATE version SET ver = :ver WHERE docName = :document", {"ver":newVer, "document":docName})          
    
    def getSummary(self):
        query = """SELECT l.name Kurs, d.docName Datei, d.hash hash, v.ver Version
                FROM lecture l, document d, version v
                WHERE l.name = d.lecture_Name AND
                d.docName = v.docName"""
        for row in self.cur.execute(query):
            print(row)
        

    def close(self):
        self.conn.commit()
        self.cur.close()
    
    def __exit__(self):
        self.conn.commit()
        self.cur.close() 

        
database = db("sqlLite.db")

data = {"Python Basic" : ["path 1", "hash 1"],
        "PythonRegEx" : ["path 2", "hash 2"],
        "PythonsqlLite" : ["path 3", "hash 3"]
        }

database.insert("SPS", data)
database.insert("DES", {"DB" : ["path 1", "hash 1"]})
database.insert("SPS", {"PythonRegEx" : ["path 4", "hash 5"]})
database.getSummary()
database.close();




