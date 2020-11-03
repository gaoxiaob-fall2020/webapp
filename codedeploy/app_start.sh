#!/bin/bash

cd /home/ubuntu/app

# Install dependecies
pip3 install -r requirements.txt

# Make migrations to the database
python3 manage.py makemigrations
python3 manage.py migrate

# Run the application
python3 manage.py runserver 0.0.0.0:8000 &