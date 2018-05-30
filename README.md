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
* Easily supports for multiple RESTful API versions.
* JWT authentication.
* Facebook login.
* Firebase Cloud Messaging integration to send push notifications.
* SQLAlchemy ORM integration and modeling of base db entities.

## Contents

* [Quick start guide](#quick-start-guide)
* [Commands](#commands)
* [Dependencies](#dependencies)
* [RESTful endpoints](#restful-endpoints)
* [FAQ](#faq)

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

3 - Move to `flask-base-main`.

```bash
cd fask-base-main
```

Before putting up and running the app containers we need to set up some environment variables which mostly are user services accounts like firebase and twilio. To do so create a file named `set_local_env_vars.sh` and add the following content replacing the values to it.

```bash
#!/usr/bin/env bash

export APP_SETTINGS="project.config.DevelopmentConfig"
export SECRET_KEY="mysecret"
export MAIL_SERVER="smtp.googlemail.com"
export MAIL_PORT="465"
export MAIL_USERNAME="my_email@my_email_domain.com"
export MAIL_PASSWORD="my_email_password"
export MAIL_DEFAULT_SENDER="my_email@my_email_domain.com"
export TWILIO_ACCOUNT_SID="1234qwer"
export TWILIO_AUTH_TOKEN="qwer1234"
export TWILIO_FROM_NUMBER="+123456789"
export CELLPHONE_VALIDATION_CODE_EXP_SECS="600"
export MAIL_USE_TLS="False"
export MAIL_USE_SSL="True"
export FCM_SERVER_KEY="9876oiuy"
```  

To set up the env variables execute:

```bash
source set_local_env_vars.sh
```

Now let's build the images and run the containers.

```bash
docker-compose build --no-cache
docker-compose up -d
```

> `docker-compose build` build the images. `--no-cache` arg indicates the cache should not be used. Docker caches the result of the build and use it in the subsequent builds. Remove this arg to build the images faster.
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

4 - Set up database

By running the following command we recreate all development db tables:

```bash
docker-compose run flask-base-service python manage.py recreate_db
```

then you can populate the db with some development useful data:

```bash
docker-compose run flask-base-service python manage.py seed_db
```

Finally test that everything works by executing the following curl command that tries to logged in using a default usr created in the seed_db command:

```bash
curl -X POST "http://0.0.0.0:5001/v1/auth/login" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"email\":\"a@a.com\",\"password\":\"password\"}"
```
> you should see something like this..
```bash
{
  "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MzAzODEzMTUsImlhdCI6MTUyNzc4OTMxNSwic3ViIjoxfQ.Dzf017g5Qf9Mi24AH-0X3womGW2koTY3c3cCO5p1djE",
  "message": "Successfully logged in.",
  "status": "success"
}
```

## Commands

### Debugging

| Command | Result |
|:---|---|
|`docker-compose logs`| Show logs of all docker-compose related containers.|
|`docker exec -ti flask-base-db psql -U postgres`| Run psql.|
|`docker-compose exec <container_name> bash`| Run bash in container_name container. See example below..|

> `docker-compose logs -f <container_name>` shows only the logs of the <container_name> container. For example `docker-compose logs -f flask-base-service` shows flask web service logs while `docker-compose logs -f flask-base-db` shows  postgresSQL db container logs.

```bash
barreto$ docker-compose exec flask-base-db bash
root@ceeb60f9aea8:/# psql -U postgres
psql (10.0)
Type "help" for help.

postgres=# \c flask_base_dev
You are now connected to database "flask_base_dev" as user "postgres".

flask_base_dev=#
```

### Base commands

| Command | Result |
|:---|---|
| `docker-compose run flask-base-service flask routes` | Show the routes for the app |
| `docker-compose run flask-base-service flask shell` | Runs a shell in the app context |

### DB Creation

| Command | Result |
|:---|---|
| `docker-compose run flask-base-service python manage.py recreate_db` | Recreates database by dropping and creating tables.|
| `docker-compose run flask-base-service python manage.py seed_db` | Seeds the database |

### DB Migrations

| Command | Result |
|:---|---|
|`docker-compose run flask-base-service flask db [OPTIONS] COMMAND [ARGS]...`| Perform database migrations. |

| COMMAND | Result |
|:---|---|
|`branches [OPTIONS]`  |Show current branch points.|
|`current [OPTIONS]`  |Display the current revision for each database.|
|`downgrade [OPTIONS] [REVISION]`  |Revert to a previous version.|
|`edit [OPTIONS] [REVISION]`  |Edit a revision file.|
|`heads [OPTIONS]`  |Show current available heads in the script directory.|
|`history [OPTIONS]`  |List changeset scripts in chronological order.|
|`init  [OPTIONS]`  |Creates a new migration repository.|
|`merge [OPTIONS] [REVISIONS]...`  |Merge two revisions together, creating a new revision file|
|`migrate [OPTIONS]`  |Autogenerate a new revision file (Alias for `revision --autogenerate`)|
|`revision [OPTIONS]`  |Create a new revision file.|
|`show [OPTIONS] [REVISION]`  |Show the revision denoted by the given symbol|
|`stamp [OPTIONS] [REVISION]`  |'stamp' the revision table with the given  revision; don't run any migrations|
|`upgrade [OPTIONS] [REVISION]` |Upgrade to a later version|

> you can see all DB migration commands documentation by executing `docker-compose run flask-base-service flask db --help`
> For a particular command documentation you can execute `docker-compose run flask-base-service flask db [COMMAND] --help`

### Run Tests

| Command | Result |
|:---|---|
|`docker-compose run flask-base-service python manage.py test`|Run integration tests|


## Dependencies

* Python v3.6.5
* Docker v18.03.1-ce
* Docker Compose v1.21.1
* Docker Machine v0.14.0
* Docker Compose file v3.6
* Flask v1.0.2
* Flask-SQLAlchemy v2.3.2
* Flask-Testing v0.7.1
* psycopg2 v2.7.3.2
* Gunicorn v19.7.1
* Nginx v1.13.8
* Bootstrap 4.0.0
* Twilio 6.8.0

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

> Endpoints implementation can be found under [/project/api/v1/auth.py](project/api/v1/auth.py).

### Cell phone number validation

| Endpoint | HTTP Method | Result |
|:---|:---:|---|
| `/cellphone`  | `POST`  | Generates cellphone_validation_code, idempotent (could be used for resend cellphone_validation_code) allows just 1 user per cellphone validation! |
| `/cellphone/verify` | `PUT` | Verifies cellphone_validation_code, idempotent (could be used many times) |

> Endpoints implementation can be found under [/project/api/v1/phone_validation.py](project/api/v1/phone_validation.py).

### Devices (Push notifications support)

| Endpoint | HTTP Method | Result |
|:---|:---:|---|
| `/devices`  | `POST`  | Creates or updates the device in the system |
| `/devices/<device_id>` | `PUT` | creates/updates and associates the device device_id to the user logged_in_user_id |

> Endpoints implementation can be found under [/project/api/v1/devices.py](project/api/v1/devices.py).

### Email validation

|Endpoint| HTTP Method | Result |
|:---|:---:|---|
| `/email_verification`  | `PUT`  | Creates a email_token_hash and sends email with token to user (assumes login=email), idempotent (could be use for resend) |
| `/email_verification/<token>` | `GET` | Sets email verified date |

> Endpoints implementation can be found under [/project/api/v1/email_validation.py](project/api/v1/email_validation.py).


## FAQ

### How do I add a new API endpoint version..?

### How do I change/add app configs?

### How does error handling works?



### How do I implement a authenticated service?

### How do I test the a endpoint?

Tests are implemented using [Flask-Testing](https://github.com/jarus/flask-testing) library. All testing files are placed under [/tests](tests). There are more than 50 test cases already implemented.

You can create a new test case class in a new file which must start with `test_` and ideally it should extend to `BaseTestCase` class which loads testing configuration and clean up db state after each test case execution. Test case method name must be prefixed with `test`.

After implementing the new test case you can run it. Go to [here](#run-tests) to see how.
