# "DayTrading Distributed System Project" 
<em>University Of Victoria  
SENG 468 - Software Scalability</em> 

## [Project Documentation](https://github.com/DockDockGoose/Project/blob/main/documentation/ProjectDocumentation.md)


##  Setup Stock Site on Docker with MongoDB !!!

### Environment
In order to use Docker, ensure you have pip, docker and mongo installed.

Before running docker-compose, ensure you are in a [python virtual environment](https://docs.djangoproject.com/en/3.1/howto/windows/#setting-up-a-virtual-environment). For example, I created a venv called `django-env`.  


On Windows from the Project directory:
```
. django-env\Scripts\activate or django-env\Scripts\activate.bat
```
On Linux/Mac from the Project directory:
```
source django-env\Scripts\activate 
```

### Docker Cleanup

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

As it is a linked volume, please ensure that the stocksite/data-db directory has been deleted prior to running the docker-compose for the first time since docker tries to preserve as much data as it can and thus retains the no root user db. By deleting, it can be freshly created by docker-compose. You can automate this db flush by uncommenting `python manage.py flush --no-input` from entrypoint.sh. The web server now waits for mongodb to be all setup before starting thanks to entrypoint.sh. 

There might be a better way to set up mongo and docker but for now, this works so yay!

### Local Docker Development

To run the development config of the application:
```
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


### Production

For production environments, we are trying Gunicorn, a production-grade WSGI server, and Nginx to act as a reverse proxy for Gunicorn to handle client requests as well as serve up static files.

To run the production containers (-d = daemon mode):
```
docker-compose -f docker-compose.prod.yml up -d --build
```

Head to http://localhost:80/ to see application running 🎉

To view logs from containers in daemon mode:
```
docker-compose -f docker-compose.prod.yml logs -f  
```
Spin down the production containers:
```
docker-compose -f docker-compose.prod.yml down -v   
```

### DockerHub

Images of our system can be found hosted on [DockerHub's](https://hub.docker.com/) registry. We have an account `dckdockgoose` with a few repositories containing images of our system, tagging each version as we develop it. To push updated versions of the images to our repositories follow the steps below.

If you are on Windows and are already logged into Docker Desktop, you wont be prompted to enter our credentials, otherwise enter them after this command:
```
docker login
```
First we have to tag the newest image containing the changes that we want to push to the registry:
```
docker tag <image-name> <repo-name>:<tag>
eg. docker tag stocksite-webapp dckdockgoose/stocksite-webapp:1.1
```
Then we can push our tagged image:
```
docker push <repo-name>:<tag>
eg. docker push dckdockgoose/stocksite-webapp:1.1
```

### Docker Images

Image               | Base              | Usage
--------------------| ------------------| ------------- 
stocksite-nginx     | nginx:latest      | Load balancer & frontend reverse proxy for Django
stocksite-webapp    | python:3          | Django stocksite API web app
<i>stocksite-mongo  | <i>mongo:latest   | <i>mongo database for Django
<i>stocksite-redis  | <i>redis:latest   | <i>cache for Django

- To follow best practice each image should be built to run as a **non-root** user and support Docker secrets.
- Eventually remove mongo-express.
- I believe we pull the base mongo image for swarm nodes, so we don't need to push a custom mongo image, I could be wrong..
- Change to overlay network for swarm.

### Docker Swarm


### API Reference

To experiment with the current API, head to http://localhost:8000/api/accounts/add and in the textfield in JSON format, enter a string username and a float amount (the amount field is optional).
```
{
    "username": "pikachu",
    "amount": 9.11
}
```
For further reference, view the README.md in the stocksite directory. You might also find the `sampleCMDS.txt` file useful when working with the API.

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
- [Dockerizing Django with Gunicron and NGINX](https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/)
- [NGINX - Django app gateway guide](https://docs.nginx.com/nginx/admin-guide/web-server/app-gateway-uwsgi-django/)

<em> When developing the app with the docker containers up and running, I find I sometimes have to prune, rebuild and re-up in order to observe all changes. It's not always the case, but it might be worth mentioning. </em>

#### TODO: 
- Add env files to gitignore. Keep secret variables secret!
- Finetune NGINX setup, look into Docker Swarm to deploy replicas of app.
- Implement other apps API endpoints.
- Update transactionNum query for all views. (maybe time var too)
- Configure custom user model. (& dynamic url routing)
- Refactor Workload Generator to send JSON requests to stocksite django app.
- Look into caching stock prices (shared cache) & local cache for recent buy/sell cmd before commits
- Look into mongodb database sharding (horizontally scale our db)



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
