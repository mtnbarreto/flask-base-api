FROM python:3.11.3-slim as base

# set working directory
# RUN mkdir -p /usr/src/app
WORKDIR /app

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# add requirements (to leverage Docker cache)
COPY requirements.txt .
# install requirements
RUN pip install -r requirements.txt

# copy project
COPY . .


# development image reusing the base
FROM base as development

CMD bash -c 'while !</dev/tcp/postgres-db/5432; do sleep 1; done; python manage.py run -h 0.0.0.0'


# Debug image reusing the base
FROM base as debug

RUN pip install debugpy

EXPOSE 5000

ENTRYPOINT [ "python", "-m", "debugpy", "--wait-for-client", "--listen", "0.0.0.0:5678", "-m", "flask", "--debug", "run", "-h", "0.0.0.0", "-p", "5000", "--no-reload"]
