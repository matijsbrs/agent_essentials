# Date: 5 March 2024
# Author: Ing. M. Behrens
# @050224_1.4.0 Major release
#                Moved the Broker class to the broker.py file
#                Improved documentation/comments


# Description: A common control object.
import json
from logging import info
from random import randint
import sys
import os
import socket
import paho.mqtt.client as mqtt
import agent_essentials.console as console
from agent_essentials.base import _version,_date
from threading import Timer, Thread
import os
from icecream import ic

class Broker():
    def __init__(self, Host, ClientId=None, Username=None, Password=None, Port=1883, Name='NoName'):
        self.Agents = {}
        if ( ClientId == None ):
            ClientId =  f"{socket.getfqdn()}.{randint(1,999)}"
        self.ClientId = ClientId
        self.Client = mqtt.Client(self.ClientId)
        self.Host = Host
        self.Port = Port
        self.Topics = []
        self.Subscribed_Topics = []
        self.Username = Username
        self.Password = Password
        if ( (Username != None ) & (Password == None)):
            self.Client.username_pw_set(self.Username)
        if ( (Username != None ) & (Password != None)):
            self.Client.username_pw_set(self.Username, self.Password)
        self._Thread = None
        self.version = _version
        self.date = _date
        self._on_message = self.on_message
        self.Debug = False
        self.Name = Name
        console.debug(f"Broker '{self.Name}' ({self.version}_{self.date}) for: {self.ClientId}")
        
    def publish(self, topic, payload):
        self.Client.publish(topic,payload)

    def on_disconnect(self):
        console.error(f"Disconnected from broker ({self.Host})")
        os._exit(0)

    def on_connect_fail(self):
        console.error(f"Could not connect to broker ({self.Host})")
        os._exit(0)

    def connect(self) -> bool:
        self.Client.on_connect = self.on_connect
        self.Client.on_message = self._on_message
        # self.Client.on_disconnect = self.on_disconnect
        self.Client.on_connect_fail = self.on_connect_fail
        self.Client.connect(self.Host, self.Port, 60)
        console.info(f"Connected to broker ({self.Host} as {self.ClientId})")
        return self.Client.is_connected()
    
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


    def _subscribe(self, topic):
        if topic not in self.Subscribed_Topics:
            # ic(topic, self.Client.subscribe(topic,2))
            state, mid = self.Client.subscribe(topic,2)
            if ( state == 0):
                console.info(f"Broker:{self.Name} subscribed to: {topic} @ {self.ClientId}")
                self.Subscribed_Topics.append(topic)
            else:
                console.error(f"Broker:{self.Name} failed to subscribe to: {topic} @ {self.ClientId}")

    def _unsubscribe(self, topic):
        if topic in self.Subscribed_Topics:
            if ( self.Client.unsubscribe(topic) == 0):
                console.info(f"Broker:{self.Name} unsubscribed from: {topic} @ {self.ClientId}")
                self.Subscribed_Topics.remove(topic)
            else:
                console.error(f"Broker:{self.Name} failed to unsubscribe from: {topic} @ {self.ClientId}")

# use the topics as a list of topics. This will set all the topics to this agent.
    def add(self, agent):
        for topic in agent.topics:
            self.Agents[topic] = agent.on_message
            self.Topics.append(topic)
            if( self.Client.is_connected() == True):
                self._subscribe(topic)
                # console.notice(f"Broker:{self.Name} subscribing to: {topic}")
                # self.Client.subscribe(topic,2)    

                
        # self.Agents[agent.topic] = agent.on_message
        # self.Topics.append(agent.topic)
        # if( self.Client.is_connected() == True):
        #     console.notice(f"Subscribing to: {agent.topic} @ {self.ClientId}")
        #     self.Client.subscribe(agent.topic,2)
        # else:
        #     self.Agents['wildcard'] = agent.on_message
        #     self.Topics = topics

    def on_message(self, client, userdata, msg):
        # t = msg.topic.split("/")
        # referenceTopic = f"{t[0]}/{t[1]}/{t[2]}/{t[3]}"
        if 'wildcard' in self.Agents:
            self.Agents['wildcard'](client, msg.topic, msg)
        else:
            if msg.topic in self.Agents:
                self.Agents[msg.topic](client, msg.topic, msg)
        
    def on_connect(self, client, userdata, flags, rc):
        console.info("Connected with result code "+str(rc))
        if ( rc == 5 ) : 
            console.warning(f"Please check credentials")
            raise ConnectionRefusedError

        for topic in self.Topics:
            # check if the topic is already subscribed
            self._subscribe(topic)
        
        return True
            
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
    