#!/bin/bash

mosquitto_pub -t zoneminder/alarme -m "`date`"
