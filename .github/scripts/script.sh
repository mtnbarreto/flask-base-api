#!/bin/bash

docker-compose exec -T flask-api python manage.py test
if [ $? -eq 0 ]
then
  echo "The script ran ok"
  exit 0
else
  echo "The script failed" >&2
  exit 1
fi