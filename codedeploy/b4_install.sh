#!/bin/bash

# Remove previous artifact
if [ -d /home/ubuntu/app ]; then sudo rm -rf /home/ubuntu/app; fi 
if [ -d /home/ubuntu/cloudwatch ]; then sudo rm -rf /home/ubuntu/cloudwatch; fi 
if [ -f /etc/nginx/sites-available/dp_ng.conf ]; then sudo rm -f /etc/nginx/sites-available/dp_ng.conf; fi