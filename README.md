# "DayTrading Distributed System Project" 
<em>University Of Victoria  
SENG 468 - Software Scalability</em> 

## [Project Documentation](https://github.com/DockDockGoose/Project/blob/main/documentation/ProjectDocumentation.md)

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
stocksite/
```
and run 
```
python manage.py runserver
```
##  Setup Stock Site on Docker

If you would like to run the application on Docker follow these steps. Please note, before starting make sure you have [docker compose](https://docs.docker.com/compose/install/) installed. 

Due to changes made to the docker containers, the previous containers need to be removed. This can be done through Docker Desktop by removing the containers under stocksite app. It can be removed through the CLI by using the commands
```
docker ps -f "status=exited" or docker ps -a -q
docker rm <container id >
```
You can also use this command but be careful it will remove all stopped containers
```
docker rm $(docker ps -a -q)
```


Go into stocksite directory and run the application:
```
cd stocksite
docker-compose build
docker-compose up
```

Head to http://localhost:8000/ to see application running 🎉

To view web and db containers:
```
docker ps
```

To get into database container:
```
docker-compose run db bash
```

Shutdown containers using `Ctrl-c` or `docker-compose down`.

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

### Testing Workload Generator with Database
If you want to test the workload generator and see the commands run on the database, here is what to do. 
First ensure you have mongodb downloaded: https://www.mongodb.com/try/download/community
And then run a local instance (specifically the Run MongoDB Community Edition part): https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/

To see what is happening on the database, I would recommend Mongodb Compass. It is a GUI of your databases. 
