#!/bin/bash

cd /home/ubuntu/app

# Install dependecies
pip3 install -r requirements.txt

# Make migrations to the database
python3 manage.py makemigrations
python3 manage.py migrate

# Run the application
screen -d -m uwsgi --socket :8001 --module webapp.wsgi
echo '******end'