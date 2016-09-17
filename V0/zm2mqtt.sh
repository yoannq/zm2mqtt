#!/bin/bash
mkfifo /tmp/pipezm2mqtt
/usr/bin/tail -f /var/log/syslog > /tmp/pipezm2mqtt &  
/usr/sbin/zm2mqtt.py /home/olimex/zoneminder2mqtt/zm2mqtt.txt &
