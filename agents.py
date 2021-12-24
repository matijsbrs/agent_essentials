# Date: 19 Decemeber 2021
# Author: Ing. M. Behrens
# Version: 1.0.1
# @161221_1.0.1 changed the quit() calles to os._exit(0) to forcefully quit. 
# Version: 1.0.2
# @161221_1.0.2 An excidental incorrect import was added which caused the script to fail. 
#               It is now removed. 
#               Added Debug option to the Broker class. When the client loop fails and Debug=True
#               Then the exception is 're'-raised. in stead of directly exiting the applicato


# Description: A common control object.
from logging import info
import sys
import os
import paho.mqtt.client as mqtt
import agent_essentials.console as console
from agent_essentials.base import _version,_date
from threading import Timer, Thread


class Agent:
    def __init__(self, Owner, DeviceId, OnUpdateReady , mqtt_client = None):
        self.mqtt_client = mqtt_client
        self.device_id = DeviceId
        self.owner = Owner
        self.topic = f"{self.owner}/{self.device_id}/+/+"
        self._on_message = self.message
        self._on_update_ready = OnUpdateReady
        self._timer     = None
        self.on_update  = None
        self.interval   = 1
        self.is_running = False
        self.version = _version
        self.date = _date
        console.debug(f"Agent ({self.version} @ {self.date}) for: {Owner}.{DeviceId}")

    def message(self, client, topic, msg):
        console.debug(f"{topic}:{msg}","Agent.message")

    def Configure(self, mqtt_client):
        self.mqtt_client    = mqtt_client
    
    def publish(self, topic, payload):
        self.mqtt_client.publish(topic,payload)

    def _run(self):
        self.on_update()
        self.is_running = False
        if self._on_update_ready != None:
            self._on_update_ready(self)

    def delayed_Update(self):
        if not self.is_running:
            self._timer = Timer(self.interval,self._run)
            self._timer.start()
            self.is_running = True


class Broker():
    def __init__(self, Host, ClientId=None, Username=None, Password=None):
        self.Agents = {}
        self.ClientId = ClientId
        if ( ClientId != None ):
            self.Client = mqtt.Client()
        else:
            self.Client = mqtt.Client(self.ClientId)
        self.Host = Host
        self.Topics = []
        self.Username = Username
        self.Password = Password
        if ( (Username != None ) & (Password != None)):
            self.Client.username_pw_set(self.Username, self.Password)
        self._Thread = None
        self.version = _version
        self.date = _date
        self._on_message = self.on_message
        self.Debug = False
        console.debug(f"Broker ({self.version}_{self.date}) for: {self.ClientId}")
        
    def publish(self, topic, payload):
        self.Client.publish(topic,payload)

    def on_disconnect(self):
        console.error(f"Disconnected from broker ({self.Host})")
        os._exit(0)

    def on_connect_fail(self):
        console.error(f"Could not connect to broker ({self.Host})")
        os._exit(0)

    def connect(self):
        self.Client.on_connect = self.on_connect
        self.Client.on_message = self._on_message
        # self.Client.on_disconnect = self.on_disconnect
        self.Client.on_connect_fail = self.on_connect_fail
        self.Client.connect(self.Host, 1883, 60)
        console.info(f"Connected to broker ({self.Host} as {self.ClientId})")
    
    def disconnect(self):
        if self.Client.is_connected() == True:
            try:
                self.Client.disconnect()
            except Exception as ex:
                console.error(f"exception: {ex}")
                console.error("Gracefull disconnecting {self.ClientId} failed.")
        os._exit(0)
        
    def subscribe(self, topic):
        self.Topics.append(topic)

    def add(self, agent):
        agent.Configure(self.Client)
        # self.Agents.append(agent)
        referenceTopic = agent.topic.replace("/+/+","")
        self.Agents[referenceTopic] = agent.on_message
        self.Topics.append(agent.topic)

    def on_message(self, client, userdata, msg):
        t = msg.topic.split("/")
        referenceTopic = f"{t[0]}/{t[1]}"
        if referenceTopic in self.Agents:
            self.Agents[referenceTopic](client, msg.topic, msg)
        
    def on_connect(self, client, userdata, flags, rc):
        console.info("Connected with result code "+str(rc))
        for topic in self.Topics:
            client.subscribe(topic,2)
            console.info(f"Subscribed to: {topic}" )
            
    def loop(self):
        try:
            self.Client.loop_forever()
        except Exception as exp:
            if self.Debug == True:
                raise exp # uncomment for debugging
            console.error(f"Broker loop failed for client:{self.ClientId} with {exp}")
            self.stop()
        finally:
            console.error(f"loop ended.")
        

    def start(self):
        self._Thread = Thread(target=self.loop)
        self._Thread.start()
    
    
    def stop(self):
        self.Client.loop_stop()
        self.disconnect()
    

    def join(self):
        if ( self._Thread != None):
            self._Thread.join()
    