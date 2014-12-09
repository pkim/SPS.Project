# -*- coding: iso-8859-1 -*-
# -*- coding: utf-8 -*-
import urllib
import ConfigParser
import re
import os
from requests import session
import sqlite3 
from macpath import curdir
import md5

#mail daniell.rotaru@gmail.com


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
                #print("Insert ", docName, list)
                self.cur.execute("INSERT INTO document VALUES(:docName, :path, :hash, :lecture_Name)", 
                                 {"docName" : docName, "path":list[0], "hash":list[1], "lecture_Name":lectureName}) 
                self.cur.execute("INSERT INTO version VALUES(:docName, :ver)", {"docName" : docName, "ver":1}) 
            else:
                #print("Update ", docName, list)
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

    def commit(self):
        self.conn.commit()
    
    def __exit__(self):
        self.conn.commit()
        self.cur.close() 

class File(object):
    def __init__(self):
        self._name = "" 
        self._url = "" 

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value


class Section(object):
    def __init__(self):
        self._name = "" 
        self._files = list()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def files(self):
        return self._files


class Course(object):
    def __init__(self):
        self._name = ""
        self._id = -1
        self._sections = list()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def url(self):
        return "https://elearning.fh-hagenberg.at/course/view.php?id=" + self.id

    @property
    def sections(self):
        return self._sections



class MoodleParser(object):

    # ctor
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('regex.conf')
        self.regex = dict(config.items('regex'))

        self.baseDir = "./elearning"
        
        if not os.path.exists(self.baseDir):
            os.makedirs(self.baseDir)

        self.database = db(self.baseDir + "/sqlLite.db")
       
        config.read('urls.conf')
        urls = dict(config.items('urls'))
        base = urls['base']
        del urls['base']

        self.urls = dict()
        for k, v in urls.items():
            self.urls[k] = base + v

        self.courses = list()
        self.ses = None

    # Properties 
    #@property
    #def loginUrl(self):
    #    return self.urls["login"]

    #@loginUrl.setter
    #def loginUrl(self, value):
    #    self.urls["login"] = value

    def plugUrls(self, conf):
               return urls

    def login(self, user, password):
        authdata = {
            'action' : 'login',
            'username' : user,
            'password' : password 
            }

        with session() as ses:
            print("")
            print("+++++ Login +++++")
            print(self.urls['login'])
            ses.post(self.urls['login'], data=authdata)
            self.ses = ses

    def fetch(self):
        self.fetchCourses()     
        print("")
        print("+++++ Fetching +++++")
        for course in self.courses:
            self.fetchCourse(course)

    def fetchCourses(self):
        print(self.urls['index'])
        result = self.ses.get(self.urls['index'])

        #a = open("index.php", "w")
        #a.write(result.text.encode("utf-8"))
        #a.close()


        if (result.status_code == 200):
            self.courses = list()
            courseBoxes = re.findall(self.regex["courses"], result.text)


            for courseBox in courseBoxes:
                course = Course()
                course.id = re.findall(self.regex["course_id"], courseBox[1])[0]
                course.name = re.findall(self.regex["course_name"], courseBox[1])[0]
                if course.id == "4568":
                    continue
                self.courses.append(course)
        else:
            print('Error')


    def fetchCourse(self, course):
        print(course.url)

        result = self.ses.get(course.url)

        #a = open(course.id + ".html", "w")
        #a.write(result.text.encode("utf-8"))
        #a.close()

        if (result.status_code == 200):
            sectionBoxes = re.findall(self.regex["section"], result.text)

            for sectionBox in sectionBoxes:
                section = Section()
                section.name = re.findall(self.regex["section_name"], sectionBox)[0]

                if section.name == 'Allgemeines':
                    continue

                fileBoxes = re.findall(self.regex["section_file"], sectionBox)
                for fileBox in fileBoxes:
                    res = File()
                    res.name = re.findall(self.regex["section_filename"], fileBox)[0]
                    res.url = re.findall(self.regex["section_fileurl"], fileBox)[0]
                    section.files.append(res)
                course.sections.append(section)
        else:
            print('Error')


    def download(self):

        for course in self.courses:
            cpath = self.baseDir + "/" + course.name
            print("")
            print("## " + course.name + " ##")
            if not os.path.exists(cpath):
                os.makedirs(cpath)
            for section in course.sections:
                spath = cpath + "/" + section.name
                print("=> " + section.name) 
                if not os.path.exists(spath):
                    os.makedirs(spath)
                for res in section.files:
                    self.handleRessource(res, section, course, spath)

            
    def handleRessource(self, res, section, course, spath):
        result = self.ses.get(res.url)
        print("handle: " + res.name)

        if (result.status_code == 200):
            headers = result.headers.keys()
            if ('content-disposition' in headers):
                #got direct link
                res.name = result.headers['content-disposition'].decode('utf-8').split(';')[1].split('=')[1].strip('"')
            else:
                #got a preview
                #ressource = re.findall(self.regex["ressource"], result.text)
                #if len(ressource) == 0:
                #    print("Error: " + res.name)
                #    return
                    
                ressource_url= re.findall(self.regex["ressource_url"], result.text)
                if len(ressource_url) == 0:
                    print("Error: " + res.name)
                    return

                res.url  = "https://elearning.fh-hagenberg.at/pluginfile.php" + ressource_url[0] 
                res.name = os.path.basename(res.url)
                
                    
            path = spath + "/" + res.name
            with open(path, 'wb') as handle:
                m = md5.new()
                result = self.ses.get(res.url, stream=True)
                m.update(result.text.encode("utf-8"))
               
                self.database.insert(course.name, {res.name : [path, m.hexdigest()]})
                self.database.commit()
        #data = {"Python Basic" : ["path 1", "hash 1"],
        #"PythonRegEx" : ["path 2", "hash 2"],
        #"PythonsqlLite" : ["path 3", "hash 3"]
        #}
       
                for block in result.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

    def close(self):
    	self.database.close()
	
    def getSummary(self):
        self.database.getSummary()


##### TESTINT #####
config = ConfigParser.RawConfigParser()
config.read('scraper.conf')
conf = dict(config.items('scraper'))

x = MoodleParser()

x.login(conf['user'], conf['pwd'])
x.fetch()
x.download()

print("")
print("#####################################################")
print("")
x.getSummary()
x.close()
