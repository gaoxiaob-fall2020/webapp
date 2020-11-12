#!/bin/bash

cd /home/ubuntu/app

# Install dependecies
pip3 install -r requirements.txt

# Make migrations to the database
python3 manage.py makemigrations
python3 manage.py migrate

# Run the application
sudo pip3 install uwsgi
uwsgi --socket :8001 --module webapp.wsgi --daemonize /opt/aws/amazon-cloudwatch-agent/logs/webapp.log
echo '******end'