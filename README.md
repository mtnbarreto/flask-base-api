# Flask Base API

This repository is part of a series of repositories that aim to create a starting point to develop a REST API using Python and Flask as main technologies.

Features:

* Development environment with Docker that supports Test-Driven Development (TDD).
* Staging, Testing, Production environments.
* RESTful API powered by Python, Flask web framework, postgres DB, rabbitmq and other technologies.
* Unit tests covering each of the REST API services.
* Code coverage.
* RESTful API documentation via Swagger.
* Easily visualize and consume RESTful API via Swagger UI.
* RabbitMQ message broker and RabbitMQ management plugin integration.


## Contents

* [Quick start guide](#quick-start-guide)
  + [Requirements](#requirements)
* [Dependencies](#dependencies)
* [RESTful endpoints](#restful-endpoints)

## Quick start guide

#### Requirements

* Docker
* Docker Compose
* Docker Machine

For mac os follow this guide to install them: https://docs.docker.com/docker-for-mac/install/


1 - Create a folder to clone all projects.

```bash
  mkdir <my_folder> && cd <myfolder>
```

2 - Clone all the projects from <myfolder> folder.

```bash
  git clone git@github.com:mtnbarreto/flask-base-api.git
  git clone git@github.com:mtnbarreto/flask-base-main.git
  git clone git@github.com:mtnbarreto/base-swagger.git
```

3 - Move to `flask-base-main`, build the images and run the containers.

In order to run the containers properly we need to set up some env variables.


```bash
cd fask-base-main
docker-compose build --no-cache
docker-compose up -d
```

> `docker-compose build` build the images. `--no-cache` arg indicates the cache should not be used. Docker caches the result of the build and use it in the subsequent builds. Remote this arg to build the images faster.
> `docker-compose up` fires up the containers. The `-d` flag is used to run the containers in the background.


Now you can check swagger RESTful API documentation visiting http://localhost:8080.
RESTful API is available under http://localhost:5001/v1. You can also use port 80 since nginx r

After running the previous commands you should be able to see all dockers containers of the app by:

```bach
docker-compose ps
```

```bash
Name                       Command                  State                                                 Ports                                           
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
celery-worker            /bin/sh -c celery -A proje ...   Up                                                                                                       
flask-base-db            docker-entrypoint.sh postgres    Up (healthy)   0.0.0.0:5435->5432/tcp                                                                    
flask-base-service       /bin/sh -c gunicorn -b 0.0 ...   Up             0.0.0.0:5001->5000/tcp                                                                    
message-broker-service   docker-entrypoint.sh rabbi ...   Up             15671/tcp, 0.0.0.0:15675->15672/tcp, 25672/tcp, 4369/tcp, 5671/tcp, 0.0.0.0:5675->5672/tcp
nginx                    nginx -g daemon off;             Up             0.0.0.0:80->80/tcp                                                                        
redis-db                 docker-entrypoint.sh redis ...   Up             0.0.0.0:6375->6379/tcp                                                                    
swagger                  sh /usr/share/nginx/docker ...   Up             0.0.0.0:8080->8080/tcp
```


> `docker-compose logs` allows us to see all docker compose containers logs.


## Commands

### Base commands

#### Show the routes for the app

```bash
docker-compose run flask-base-service flask routes
```

#### Runs a shell in the app context

```bash
docker-compose run flask-base-service flask shell
```

### Migrations

#### Perform database migrations

```bash
docker-compose run flask-base-service db [OPTIONS] COMMAND [ARGS]...
```

> docker-compose run flask-base-service flask db --help

```bash
Commands:
  branches   Show current branch points
  current    Display the current revision for each...
  downgrade  Revert to a previous version
  edit       Edit a revision file
  heads      Show current available heads in the script...
  history    List changeset scripts in chronological...
  init       Creates a new migration repository.
  merge      Merge two revisions together, creating a new...
  migrate    Autogenerate a new revision file (Alias for...
  revision   Create a new revision file.
  show       Show the revision denoted by the given...
  stamp      'stamp' the revision table with the given...
```


### How to recreate the database

There is a command already implemented in the RESTful API. To run the command we should invoke it through `flask-base-service` container as the following command shows. Basically the commands runs `python manage.py recreate_db` in `flask-base-service` container.

```bash
docker-compose run flask-base-service python manage.py recreate_db
```

> Development, Testing and Production db are automatically created when db container runs so the first time we run the app we don't need to recreate the db.

#### How to run tests





## Dependencies

* Python v3.6.5
* Docker v18.03.1-ce
* Docker Compose v1.21.1
* Docker Machine v0.14.0
* Docker Compose file v3.6
* Flask v1.0.2
* Flask-SQLAlchemy v2.3.2
* Flask-Testing v0.6.2
* psycopg2 v2.7.3.2
* Gunicorn v19.7.1
* Nginx v1.13.8
* Bootstrap 4.0.0

## RESTful endpoints

### Sanity Check

| Endpoint | HTTP Method | Result |
|:---|:---:|---|
| `/ping`  | `GET` | Sanity check  |

### Authentication

| Endpoint | HTTP Method | Result |
|:---|:---:|---|
| `/auth/register`  | `POST`  | Registers a new user  |
| `/auth/login`  | `POST`  | Login the user  |
| `/auth/logout`  | `GET`  | User logout  |
| `/auth/status`  | `GET`  | Returns the logged in user's status  |
| `/auth/password_recovery`  | `POST`  | Creates a password_recovery_hash and sends email to user |
| `/auth/password`  | `PUT`  | Reset user password  |
| `/auth/password_change`  | `PUT`  | Changes user password  |
| `/auth/facebook/login`  | `POST`  | Logs in user using fb_access_token returning the corresponding JWT. if user does not exist registers/creates a new one  |
| `/auth/facebook/set_standalone_user`  | `PUT`  | Sets username and password to work directly on the system without facebook  |

### Cell phone number validation

| Endpoint | HTTP Method | Result |
|:---|:---:|---|
| `/cellphone`  | `POST`  | Generates cellphone_validation_code, idempotent (could be used for resend cellphone_validation_code) allows just 1 user per cellphone validation! |
| `/cellphone/verify` | `PUT` | Verifies cellphone_validation_code, idempotent (could be used many times) |

### Devices (Push notifications support)

| Endpoint | HTTP Method | Result |
|:---|:---:|---|
| `/devices`  | `POST`  | Creates or updates the device in the system |
| `/devices/<device_id>` | `PUT` | creates/updates and associates the device device_id to the user logged_in_user_id |

### Email validation

|Endpoint| HTTP Method | Result |
|:---|:---:|---|
| `/email_verification`  | `PUT`  | Creates a email_token_hash and sends email with token to user (assumes login=email), idempotent (could be use for resend) |
| `/email_verification/<token>` | `GET` | Sets email verified date |
