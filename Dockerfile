FROM python:3.8.2 as base

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements (to leverage Docker cache)
ADD ./requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install --no-cache-dir -r requirements.txt
# env variables
ENV FLASK_ENV="docker"
ENV FLASK_APP=project/__init__.py
# add app
ADD . /usr/src/app



# DEBUG image
FROM base as debug
# Debug image reusing the base
# Install dev dependencies for debugging
RUN pip install debugpy
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1



# PRODUCTION image
FROM base as prod
# run server
CMD gunicorn -b 0.0.0.0:5000 manage:app --reload
