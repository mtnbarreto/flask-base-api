FROM python:3.6.3

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements (to leverage Docker cache)
ADD ./requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# add app
ADD . /usr/src/app

# run server
CMD gunicorn -b 0.0.0.0:5000 manage:app --reload

# CMD python manage.py runserver -h 0.0.0.0

# CMD export FLASK_APP=project/__init__.py
# CMD flask run --host=0.0.0.0
