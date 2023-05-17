FROM python:3.11.3-slim

RUN mkdir -p /app
WORKDIR /app

# add requirements (to leverage Docker cache)
ADD ./flask-api/requirements.txt /app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

ADD ./flask-api/ /app/

ENTRYPOINT celery -A project.celery worker --loglevel=INFO --pool=prefork -E
