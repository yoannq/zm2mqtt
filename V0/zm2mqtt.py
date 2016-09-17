#!/usr/bin/python

import daemon
import time
import subprocess as sp
import urlparse
import re
import ConfigParser
import sys
import mysql.connector
import mosquitto, urlparse

config = ConfigParser.RawConfigParser()
config.read(sys.argv[1])

   
        

mqtt_url = config.get('mqtt', 'mqtt_url')
mqtt_publish_str = config.get('mqtt', 'mqtt_publish_str')

url = urlparse.urlparse(mqtt_url)
# Connect
mqttc = mosquitto.Mosquitto()
mqttc.username_pw_set(url.username, url.password)
mqttc.connect(url.hostname, url.port)
mqttc.publish(mqtt_publish_str+str("info"), "connected")


def process_syslog():
	regex1=re.compile('Closing event (\d+), alarm end\]')
	pipe_tail =  open("/tmp/pipezm2mqtt", 'r', 0)
	pipe_tail.flush()
	while True:
		data = pipe_tail.readline()
		data=re.sub("\n","",data)
		match = regex1.findall(data)
		if len(match)>0:
			event_num=int(match[0])
			time.sleep(3)
			conn = mysql.connector.connect(host="localhost",user="zmuser",password="zmpass", database="zm")
			cur = conn.cursor()
			cur.execute("SELECT * FROM Events")
			for row in cur.fetchall():
					NumCamera=row[1]
					TotScore=row[11]
					AvgScore=row[12]
					MaxScore=row[13]
					if int(row[0])==event_num:
							mqttc.connect(url.hostname, url.port)
							mqttc.publish(mqtt_publish_str+str("NumCamera"), NumCamera)
							mqttc.publish(mqtt_publish_str+str("Event_num"), event_num)
							mqttc.publish(mqtt_publish_str+str("TotScore"), TotScore)
							mqttc.publish(mqtt_publish_str+str("AvgScore"), AvgScore)
							mqttc.publish(mqtt_publish_str+str("MaxScore"), MaxScore)
							mqttc.publish(mqtt_publish_str+str("Synthese"), str(NumCamera)+";"+str(event_num)+";"+str(MaxScore)+";"+str(AvgScore))
							mqttc.loop(2) 
			cur.close()
			conn.close()

def run():
	#with daemon.DaemonContext():
		process_syslog()

if __name__ == "__main__":
	run()
