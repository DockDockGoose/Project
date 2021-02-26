# "DayTrading Distributed System Project" 
<em>University Of Victoria  
SENG 468 - Software Scalability</em> 

## [Project Documentation](https://github.com/DockDockGoose/Project/blob/main/documentation/ProjectDocumentation.md)


##  Setup Stock Site on Docker with MongoDB !!!

In order to use Docker, ensure you have pip, docker and mongo installed.

Before running docker-compose, we have to be in the Django virtual environment. Daniel had previously set up `django-project` but I faced some issues with using/activating that, so I created another venv called `django-env`.  

If you face any issues with the following command, simply [create your own venv for Django](https://docs.djangoproject.com/en/3.1/howto/windows/#setting-up-a-virtual-environment).

On Windows from the Project directory:
```
. django-env\Scripts\activate or django-env\Scripts\activate.bat
```
On Linux/Mac from the Project directory:
```
source django-env\Scripts\activate 
```

Due to changes made to the docker containers, the previous containers need to be removed. This can be done through Docker Desktop by removing the containers under stocksite app. It can be removed through the CLI by using the commands
```
docker ps -f "status=exited" or docker ps -a -q
docker rm <container id >
```
You can also use this command but be careful it will remove all stopped containers 
```
docker rm $(docker ps -a -q)
```
It is recommended we prune the system to clear all old/previous containers, images & volumes that docker might try to use again for our project. <b>Be careful as this removes all of the items listen above.</b>

To prune the system:
```
docker system prune -af
```

Note that mongo-express will initially fail in connecting to the mongo container (& db). This is because the root user must be created first.
This user is created through the docker entrypoint script that is mounted as mongo-init.js. 
In order for the script and dockerfiles to run correctly, we have to run a fresh docker instance of the database. 

As it is a linked volume, please ensure that the stocksite/data-db directory has been deleted prior to running the docker-compose for the first time since docker tries to preserve as much data as it can and thus retains the no root user db. By deleting, it can be freshly created by docker-compose.

There might be a better way to set up mongo and docker but for now, this works so yay!


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

To use MongoExpress and view our db in a browser head to http://localhost:8081


To look at our database and its collections on the CLI, first enter the mongo shell of the docker container as root:
```
docker exec -it mongodb mongo -u root
```
You will be prompted to enter our team password. After entering it, you have succesfully accessed our contianerized db!
``` 
show dbs
use mongodb
show collections
```
Use `exit` to leave mongo shell. 

Shutdown containers using `Ctrl-c` or `docker-compose down`.

To experiment with the current API, head to http://localhost:8000/api/accounts/add and in the textfield in JSON format, enter a string username and a float amount (the amount field is optional).
```
{
    "username": "pikachu",
    "amount": 9.11
}
```

### REST-ful resources 😉:

- [Django REST Framework (DRF) official documentation.](https://www.django-rest-framework.org/#example)
- [Detailed descriptions, with full methods and attributes, for each of Django REST Framework's class-based views and serializers. (clean, browsable UI)](http://www.cdrf.co/)
- [Django documentation on models and databases.](https://docs.djangoproject.com/en/3.1/topics/db/)
- [Djongo documentation, specifically model queries and database transactions.](https://www.djongomapper.com/djongonxt-model-query/)
- [The documentation for the Django user registration/authentication module we are currently using.](https://django-rest-auth.readthedocs.io/en/latest/installation.html)
- [Awesome slides on MongoDB schema design best practices.](https://speakerdeck.com/joekarlsson/mongodb-schema-design-best-practices?slide=50)
- [A quick but detailed tutorial for creating API endpoints in Django.](https://www.caktusgroup.com/blog/2019/02/01/creating-api-endpoint-django-rest-framework/)
- [A tutorial on building a CRUD API (app) with React and Django using DRF (something we could do for the front-end @Daniel)](https://blog.logrocket.com/creating-an-app-with-react-and-django/)
- [DRF caching viewsets & apiviews](https://www.django-rest-framework.org/api-guide/caching/)
- [DRF synchronous caching using rq tasks](https://django-cacheback.readthedocs.io/en/latest/)

<em> When developing the app with the docker containers up and running, I find I sometimes have to prune, rebuild and re-up in order to observe all changes. It's not always the case, but it might be worth mentioning. </em>

#### TODO: 
- Update Transactions to log the correct stock object changes.
- Enable serving multiple concurrent users with nginx & uwsgi.
- Implement other apps API endpoints.
- Configure custom user model. (& dynamic url routing)
- Refactor Workload Generator to send JSON requests to stocksite django app.
- Look into caching stock prices (shared cache) & local cache for recent buy/sell cmd before commits
- Look into mongodb database sharding (horizontally scale our db)

## Local Setup Information
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

## Workload Generator
Takes workload input file and partitions commands per user, retaining transaction number, 
command, stock symbol and other related information.
Writes each partition to a file in the format of ```[user].txt```. Each partition file is read and a thread is spawned per user (the WG dynamically adjusts the port number). 
The files are parsed and the requested commands are sent in JSON format to the specified server.

<em>The default server and port is ```localhost:65432```</em>

To run using the default 1 user workload file:
```
python3 workload_gen.py
```
To run using a specific workload file (eg. WL_2_USER.txt):
```
python3 workload_gen.py ../workloads/WL_2_USER.txt
```


## Running the Python WebServer & Load Balancer
This python webserver will immediately spin up and start accepting client requests. 

<em>The default server and port is ```localhost:65432```</em>

To run the web server call the following command, and input the server address, and port when prompted. 
```
python3 web_server.py
```

To run the load balancer call the below command. You will be prompted to enter each webservers hostname and port. 
```
python3 load_balancer.py
```

Notes: 
 * to send simulated requests to the webserver see workload generator section above. 
 * To end the server I use (ctrl+ALT+(BREAK/PAUSE)), maybe CRTL+Z, CRTL+C would work for different users

### Testing Workload Generator with Database on VM
If you want to test the workload generator and see the commands run on the database, here is what to do. 
First ensure you have mongodb installed and pymongo to interact with the databse (reference: https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-18-04 )

```
sudo apt update

sudo apt install -y mongodb

sudo apt install python3-pip

pip3 install pymango

```

The installation should automatically starts a mongodb instance. Here are some commands to check that it is  running properly. 
```

# Check status to make sure it is running
sudo systemctl status mongod
# Check the database has the right server address and port
mongo --eval 'db.runCommand({ connectionStatus: 1 })'
# Connect to mongo db instance
mongo 
```

To look at our database and its collections (reference: https://docs.mongodb.com/manual/reference/mongo-shell/ )
```
show dbs
use mongodb
show collections
```
Use `exit` to leave mongo shell. 

If the mongodb instance is not running, here the is command to start it:
```
sudo systemctl start mongod

```

Command to shutdown mongodb instance
```
sudo systemctl stop mongodb
```

I would also highly recommend Mongodb Compass. It is a GUI for Mongodb: https://www.mongodb.com/try/download/compass 
