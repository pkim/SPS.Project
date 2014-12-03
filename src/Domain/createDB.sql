""CREATE TABLE if not exists lecture (name varchar(100) primary key);
CREATE TABLE if not exists document
(
  docName varchar(100) primary key,
  path varchar(200),
  hash varchar(200),
  lecture_Name varchar(100),
  constraint lecture_Name foreign key (lecture_Name) references lecture(name)
);""
