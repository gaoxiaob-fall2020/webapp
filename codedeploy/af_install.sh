#!/bin/bash

# Setup AWS CloudWatch
sudo cp /home/ubuntu/cloudwatch/amazon-cloudwatch-agent.json \
/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
    -s

# Create log file for webapp
sleep 30
sudo touch /opt/aws/amazon-cloudwatch-agent/logs/webapp.log
sudo chown ubuntu:ubuntu /opt/aws/amazon-cloudwatch-agent/logs/webapp.log


sudo ln -s /etc/nginx/sites-available/dp_ng.conf /etc/nginx/sites-enabled/
sudo /etc/init.d/nginx restart