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
command_tail_config = config.get('taillog', 'commande')
command_tail = re.split(" ",str(command_tail_config))

mqtt_url = config.get('mqtt', 'mqtt_url')
mqtt_publish_str = config.get('mqtt', 'mqtt_publish_str')

url = urlparse.urlparse(mqtt_url)
# Connect


def process_syslog():


	try :
		pipe_tail = sp.Popen(command_tail, stdout = sp.PIPE)        
		pipe_tail.stdout.flush()     
		mqttc = mosquitto.Mosquitto()
		mqttc.username_pw_set(url.username, url.password)
		mqttc.connect(url.hostname, url.port)
		mqttc.publish(mqtt_publish_str+str("info"), "connected")
		
		regex1=re.compile('Closing event (\d+), alarm end\]')
		while True:
			data = pipe_tail.stdout.readline()
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
		mqttc.disconnect()
	except :
		raise
		time.sleep(30)
			
def run():
	while True:
		process_syslog()

if __name__ == "__main__":
	run()
