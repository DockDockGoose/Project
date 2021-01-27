# "DayTrading Distributed System Project" 

### School: University Of Victoria  
### Class: SENG 468 Software Scalability 

___

Technologies (Bolded are our choices)
#### Web Framework
 * **DJango**
 * Flask

#### Containerization  
 * **Docker**

#### DataBase Management 
 * **PostGres**
 * MongoDB
#### Languages
 * **Python**
 * Java
 * Go

#### Libraries
 * **WSGI**


## Setup Information
 [Follow these instructions to set up Django](https://docs.djangoproject.com/en/3.1/topics/install/#installing-official-release)
 
Make sure you have [pip](https://pip.pypa.io/en/stable/) installed.

Project is in the stocksite folder. 

Before running a local instance, you have to run 

```
django-project\Scripts\activate
```

then you can go into 
```
stocksite/dir
```
and run 
```
python manage.py runserver
```


## Workload Generator
Takes workload input file and partitions commands per user, retaining transaction number, 
command, stock symbol and other related information.
Writes each partition to a file in the format of ```[user].txt```. Each partition file is read and a thread is spawned per user (the WG dynamically adjusts the port number). 
The files are parsed and the requested commands are sent in JSON format to the specified server.

<em>The default server and port is ```localhost:44444```</em>

To run using the default 1 user workload file:
```
python3 workload_gen.py
```
To run using a specific workload file (eg. WL_2_USER.txt):
```
python3 workload_gen.py ../workloads/WL_2_USER.txt
```


## Tasks
- [x] Frontend setup (Django)
- [ ] Backend setup (wsgi/apache?)
- [x] Workgenerator -- Dianna  
- [ ] Server -- Damon/Daniel
- [ ] Data Base Querying.  -- Daniel
- [ ] Database Schema  - Sam