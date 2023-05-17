[![Docker Image CI](https://github.com/mtnbarreto/flask-base-api/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/mtnbarreto/flask-base-api/actions/workflows/docker-image.yml)
# Flask Base API

This repository aim to create a starting point to develop a REST API using Python and Flask framework as main technologies.

Features:

* Development environment with Docker that supports Test-Driven Development (TDD).
* Staging, Testing, Production environments.
* RESTful API powered by Python, Flask web framework, postgres DB, rabbitmq and other technologies.
* Unit tests covering the REST API services.
* Code coverage.
* RESTful API documentation via Swagger.
* Easily visualize and consume RESTful API via Swagger UI.
* RabbitMQ message broker and RabbitMQ management plugin integration.
* Easily supports for multiple RESTful API versions.
* JWT authentication.
* Facebook login.
* Google login.
* Firebase Cloud Messaging integration to send push notifications.
* SQLAlchemy ORM integration and modeling of base db entities.
* pgAdmin db administration and development platform for PostgreSQL.
* nginx reverse proxy and load balancer. 

## Contents

* [Quick start guide](#quick-start-guide)
* [Commands](#commands)
* [Dependencies](#dependencies)
* [RESTful endpoints](#restful-endpoints)
* [FAQ](#faq)

## Quick start guide

 
#### 1 - Create a folder to clone all projects.

```bash
  mkdir <my_folder> && cd <myfolder>
```

#### 2 - Clone the project from <myfolder> folder.

```bash
  git clone git@github.com:mtnbarreto/flask-base-api.git
```


#### 3 - Set up environment variables

Before putting up and running the app containers we need to set up some environment variables which mostly are user services accounts like firebase and twilio. To do so create a file named `set_local_env_vars.sh` and add the following content replacing the values to it.

```bash
#!/usr/bin/env bash

export APP_SETTINGS="project.config.DevelopmentConfig"
export FLASK_APP=project/__init__.py
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
source ../set_local_env_vars.sh
```
#### 4 - Move to `flask-main`.

```bash
cd flask-main
```


#### 5 - Now let's build the images and run the containers. `flask-base-api` requires docker 20.10.1 or newer. 

```bash
docker-compose build --no-cache
docker-compose up -d
```

> `docker-compose build` build the images. `--no-cache` arg indicates the cache should not be used. Docker caches the result of the build and use it in the subsequent builds. Remove this arg to build the images faster.
> `docker-compose up` fires up the containers. The `-d` flag is used to run the containers in the background.

`docker-compose up -d` should output something like ...

```bash
Creating network "flask-main_default" with the default driver
Creating pgadmin       ... done
Creating redis         ... done
Creating postgres-db   ... done
Creating rabbitmq      ... done
Creating celery-worker ... done
Creating flask-api     ... done
Creating swagger       ... done
Creating nginx         ... done
```

After running the previous commands, let see the list of container by running:

```bash
docker-compose ps
```

```bash
Name                       Command                  State                                                 Ports                                           
-------------------------------------------------------------------------------------------------------------------------------------------------------------------
flask-api             /bin/sh -c bash -c 'while  ...   Up             0.0.0.0:5001->5000/tcp, 0.0.0.0:5678->5678/tcp                                                 
celery-worker         /bin/sh -c celery -A proje ...   Up                                                                                                            
postgres-db           docker-entrypoint.sh postgres    Up (healthy)   0.0.0.0:5435->5432/tcp                                                                         
nginx                 /docker-entrypoint.sh ngin ...   Up             0.0.0.0:80->80/tcp                                                                             
pgadmin               /entrypoint.sh                   Up             443/tcp, 0.0.0.0:5050->80/tcp                                                                  
rabbitmq              docker-entrypoint.sh rabbi ...   Up             15671/tcp, 0.0.0.0:15675->15672/tcp, 15691/tcp, 15692/tcp, 25672/tcp, 4369/tcp, 5671/tcp,      
                                                                      0.0.0.0:5675->5672/tcp                                                                         
redis           docker-entrypoint.sh redis ...   Up             0.0.0.0:6375->6379/tcp                                                                         
swagger         sh /usr/share/nginx/docker ...   Up             0.0.0.0:8080->8080/tcp 
```

Make sure all services started properly. `State` should be `Up`.  

#### 6 - Set up database

By running the following command we recreate all development db tables:

```bash
docker-compose exec flask-api python manage.py recreate_db
```

then you can populate the db by executing the following command:

```bash
docker-compose exec flask-api python manage.py seed_db
```

Finally test that everything works by executing the following curl command that tries to logged in using a user created by the seed_db command:

```bash
curl -X POST "http://0.0.0.0/v1/auth/login" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"email\":\"a@a.com\",\"password\":\"password\"}"
```

it should output something like this:

```json
{
  "status":"success",
  "message":"Successfully logged in.",
  "auth_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODY2NzU2MzMsImlhdCI6MTY4NDA4MzYzMywic3ViIjoxfQ.t8QKjoNfP3GuCLpCLVW-sPeEynHtX8Vk7DaOfVn0tWU",
  "username":"martin"
}
```

## Commands

### Debugging

| Command | Result |
|:---|---|
|`docker-compose logs`| Shows logs of all docker-compose related containers.|
|`docker exec -ti postgres-db psql -U postgres`| Runs psql.|
|`docker-compose exec <container_name> bash`| Runs bash in container_name container. See example below.|

> `docker-compose logs -f <container_name>` shows only the logs of the <container_name> container. For example `docker-compose logs -f flask-api` shows flask web service logs while `docker-compose logs -f postgres-db` shows  postgresSQL db container logs.

```bash
barreto$ docker-compose exec postgres-db bash
root@ceeb60f9aea8:/# psql -U postgres
psql (10.0)
Type "help" for help.

postgres=# \c db_dev
You are now connected to database "db_dev" as user "postgres".

db_dev=#
```



### Base commands

| Command | Result |
|:---|---|
| `docker-compose exec flask-api flask routes` | Shows the app's endpoints list |
| `docker-compose exec flask-api flask shell` | Runs a shell in the app context |

### DB Creation

| Command | Result |
|:---|---|
| `docker-compose exec flask-api python manage.py recreate_db` | Recreates database by dropping and creating tables.|
| `docker-compose exec flask-api python manage.py seed_db` | Seeds the database |


### DB Migrations

| Command | Result |
|:---|---|
|`docker-compose exec flask-api flask db [OPTIONS] COMMAND [ARGS]...`| Perform database migrations. |

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

> you can see all DB migration commands documentation by executing `docker-compose run flask-api flask db --help`
> For a particular command documentation you can execute `docker-compose run flask-api flask db [COMMAND] --help`

### Run Tests

| Command | Result |
|:---|---|
|`docker-compose exec flask-api python manage.py test`| Runs all integration tests|
|`docker-compose exec flask-api python manage.py test <file-name or pattern>`| Runs all integration tests that matches the file-name or pattern |

> Make sure you run tests on `development` target. It does not work on `debug` target which uses debugpy library.
> There are more than 55 integration test covering the REST endpoints. Check out test implementations inside [test](/flask-api/tests/) folder.

The most conveniend way to run test on demand is by using VSCode UI. 

![vs-code UI testing](.github/files/ui-tests.gif)


## Dependencies

* Python 3.11.3
* Docker 20.10.11+
* Docker Compose 1.29.2+
* Flask v2.3.2

For a full list of python dependencies check out [requiremets.txt](/flask-api/requirements.txt) file.


## RESTful endpoints

Run `docker-compose exec flask-api flask routes` to see the REST API endpoints list.

```bash
Endpoint                                    Methods  Rule                                 
------------------------------------------  -------  -------------------------------------
auth.facebook_login                         POST     /v1/auth/facebook/login              
auth.get_user_status                        GET      /v1/auth/status                      
auth.login_user                             POST     /v1/auth/login                       
auth.logout_user                            GET      /v1/auth/logout                      
auth.password_change                        PUT      /v1/auth/password_change             
auth.password_recovery                      POST     /v1/auth/password_recovery           
auth.password_reset                         PUT      /v1/auth/password                    
auth.register_user                          POST     /v1/auth/register                    
auth.set_standalone_user                    PUT      /v1/auth/facebook/set_standalone_user
devices.connect_device_with_logged_in_user  PUT      /v1/devices/<device_id>              
devices.register_device                     POST     /v1/devices                          
email_validation.email_verification         PUT      /v1/email_verification               
email_validation.verify_email               GET      /v1/email_verification/<token>       
phone_validation.register_user_cellphone    POST     /v1/cellphone                        
phone_validation.verify_user_cellphone      PUT      /v1/cellphone/verify                 
static                                      GET      /static/<path:filename>              
users.add_user                              POST     /v1/users                            
users.get_all_users                         GET      /v1/users                            
users.get_single_user                       GET      /v1/users/<user_id>                  
users.ping_pong                             GET      /v1/ping                             
users.push_echo                             POST     /v1/push_echo      
```

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

`flask-base-api` supports backwards compatibility, which is crucial for mobile api development. API services are added under [/v1](/flask-api/project/api/v1/) url prefix by default. 

In order to update endpoints and still support v1, simply regist blueprints with url-prefix `/v2` and do not change `/v1` endpoints. Whenever an endpoint needs to be updated, copy `v1` version and paste it in `v2` project folder, then make necesarry changes over `v2`. 

```python
    app.register_blueprint(auth_blueprint, url_prefix='/v1')
    app.register_blueprint(auth_blueprint2, url_prefix='/v2')
    ...
    ..
    .
```

### How do I change/add app configs?

`flask-base-api` support multiple environments. Check out config values at [/flask-api/project/config.py](/flask-api/project/config.py).

### How does error handling works?

`flask-base-api` registers multiple error handlers for most common exceptions types.

```python
    # register error handlers
    from project.api.common.utils import exceptions
    from project.api.common import error_handlers
    InvalidPayload, error_handlers.handle_exception)
    app.register_error_handler(exceptions.BusinessException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.UnauthorizedException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.ForbiddenException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.NotFoundException, error_handlers.handle_exception)
    app.register_error_handler(exceptions.ServerErrorException, error_handlers.handle_exception)
    app.register_error_handler(Exception, error_handlers.handle_general_exception)
```

 You can raise `InvalidPayload`, `BusinessException`, `UnauthorizedException`, `ForbiddenException`, `NotFoundException`, `ServerErrorException` from within endpoint implementations with is formated into json  format by error handlers. For instance: 

 ```python
  raise UnauthorizedException(message='Something went wrong. Please contact us.')
 ```

and error handler returns 

> 401 Unauthorized

```json
{"message":"Something went wrong. Please contact us.","status":"error"}
```

You can easily implement custom exception by extending `APIException` type, which is the same type that `flask-base-api` exceptions extends.

```python
class APIException(Exception):

    def __init__(self, message, status_code, payload):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv
```

We can return a response message for the new exception type by registering a handler like:

```python
app.register_error_handler(MyNewException, error_handlers.handle_general_exception)
``` 

### How do I implement a authenticated service?

`flask-base-api` use JWT authentication. 

By using `@authenticate` decorator you can easily force JWT check and authentication for the endpoint like the following method indicates. If authentication goes well, `user_id` is passed as argument to the endpoint function. If something goes wrong, it raise `UnauthorizedException()` and server responds with a 401 Unauthorized response.

```python
@phone_validation_blueprint.route('/cellphone/verify', methods=['PUT'])
@accept('application/json')
@authenticate
def verify_user_cellphone(user_id: int):
    ''' verifies cellphone_validation_code, idempotent (could be used many times) '''
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayload()
    validation_code = post_data.get('validation_code')
    user = User.get(user_id)
    ...
    ..
    .
```

Curious about how the `@authenticate`  decorator is implemented?

```python
def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise UnauthorizedException()
        auth_token = auth_header.split(" ")[1]
        user_id = User.decode_auth_token(auth_token)
        user = User.get(user_id)
        if not user or not user.active:
            raise UnauthorizedException(message='Something went wrong. Please contact us.')
        return f(user_id, *args, **kwargs)
    return decorated_function
```


### How do I test the a endpoint?

Tests are implemented using [Flask-Testing](https://github.com/jarus/flask-testing) library. All testing files are placed under [/tests](tests). There are more than 50 test cases already implemented.

You can create a new test case class in a new file which must start with `test_` and ideally it should extend to `BaseTestCase` class which loads testing configuration and clean up db state after each test case execution. Test case method name must be prefixed with `test`.

After implementing the new test case you can run it. Go to [here](#run-tests) to see how.

### How do I use swagger to play with the API?


Now you can check swagger RESTful API documentation visiting http://localhost:8080.

![swagger](.github/files/swagger.png)

RESTful API is available under http://localhost:5001/v1. You can also use port 80 since nginx was also set up. [http://localhost/v1/ping](http://localhost/v1/ping) should return `{"status":"success","message":"pong!"}`.


### How do I use pgAdmin?

First get the postgres db ip address by executing

```bash
docker inspect postgres-db | grep "IPAddress"
```

which outputs the `IPAddress`

```bash
  "SecondaryIPAddresses": null,
  "IPAddress": "",
          "IPAddress": "192.168.224.3",
```

Then open `pgAdmin` in your browser `http://0.0.0.0:5050/`, and login  by using email: `admin@admin.com`, password: `password` credentials.

Then connect to db server using the ip address retrieved above and  using the following postgres credentials: user: `postgres`, password: `postgres`.

![pgAdmin](.github/files/pgAdmin.png)