#!/usr/bin/python
# version 2

import time
import subprocess as sp
import urlparse
import re
import ConfigParser
import sys
import mysql.connector
import mosquitto, urlparse
import os
import syslog
import glob
			
def run():
    
    try :
        syslog.syslog('Process started')
        path_to_event_files=sys.argv[1]
        syslog.syslog('Path to event files : '+path_to_event_files) 
        #get event number
        a=os.path.basename(glob.glob(path_to_event_files+"/.*")[0])
        event_number=a[1:]
        syslog.syslog('Event number : '+event_number)  

        config = ConfigParser.RawConfigParser()
        config.read("/home/olimex/zm2mqtt/zm2mqtt.txt")
        
        mqtt_url = config.get('mqtt', 'mqtt_url')
        mqtt_publish_str = config.get('mqtt', 'mqtt_publish_str')
        syslog.syslog('Mosquitto config : '+mqtt_url)  
        syslog.syslog('Mosquitto config : '+mqtt_publish_str)          
        
        url = urlparse.urlparse(mqtt_url)


        mqttc = mosquitto.Mosquitto()
        mqttc.username_pw_set(url.username, url.password)
        mqttc.connect(url.hostname, url.port)
        mqttc.publish(mqtt_publish_str+str("info"), "connected")
        
        conn = mysql.connector.connect(host="localhost",user="zmuser",password="zmpass", database="zm")
        cur = conn.cursor()
        cur.execute("SELECT * FROM Events")
        for row in cur.fetchall():
            NumCamera=row[1]
            TotScore=row[11]
            AvgScore=row[12]
            MaxScore=row[13]
            EventType=row[20]
            if int(row[0])==int(event_number):
                mqttc.connect(url.hostname, url.port)
                if str(EventType) == "Signal: Reacquired":
                #if 1:
                    print row[0],EventType
                    TotScore=-1
                    AvgScore=-1
                    MaxScore=-1



                mqttc.publish(mqtt_publish_str+str("NumCamera"), NumCamera)
                mqttc.publish(mqtt_publish_str+str("EventNum"), event_number)                
                mqttc.publish(mqtt_publish_str+str("EventType"), str(EventType))
                mqttc.publish(mqtt_publish_str+str("TotScore"), TotScore)
                mqttc.publish(mqtt_publish_str+str("AvgScore"), AvgScore)
                mqttc.publish(mqtt_publish_str+str("MaxScore"), MaxScore)
                mqttc.publish(mqtt_publish_str+str("Synthese"), str(NumCamera)+";"+str(event_number)+";"+str(MaxScore)+";"+str(AvgScore))


                mqttc.loop(2) 
                mqttc.disconnect()

        cur.close()
        conn.close()

    except:
        syslog.syslog(syslog.LOG_ERR, 'Error')
        raise
    
    
    
if __name__ == "__main__":
	run()
