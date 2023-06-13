# Date: 19 Decemeber 2021
# Author: Ing. M. Behrens
# Version: 1.0.1
# @161221_1.0.1 changed the quit() calles to os._exit(0) to forcefully quit. 
# Version: 1.0.2
# @161221_1.0.2 An excidental incorrect import was added which caused the script to fail. 
#               It is now removed. 
#               Added Debug option to the Broker class. When the client loop fails and Debug=True
#               Then the exception is 're'-raised. in stead of directly exiting the applicato
# @201222_1.2.3 Minor changes to improve mqtt integration
#                minor release is comming up.
# @211222_1.2.5 moved some of the 'private' properties to public. 
#                renamed self.message -> self.on_message to identify it as a handler
#                the default topic is changed -> {owner}/{device_id}/# was {owner}/{device_id}/+/+
#                #TODO on_message / reference topic is still a bit of a bodge job. needs cleaning up.
# @221222_1.3.0 Nieuw minor release. 
#                Improved documentation

# Description: A common control object.
from logging import info
from random import randint
import sys
import os
import socket
import paho.mqtt.client as mqtt
import agent_essentials.console as console
from agent_essentials.base import _version,_date
from threading import Timer, Thread


class Agent:
    mqtt_client = None
    topic = None
    _on_message = None
    _on_update_ready = None
    timer     = None
    on_update  = None
    interval   = 1
    is_running = False
    version = _version
    date = _date

    def __init__(self) -> None:
        console.notice(f"basic agent ({self.version} @ {self.date})")


    def __init__(self, topic, OnUpdateReady , mqtt_client = None):
        self.mqtt_client = mqtt_client
        # self.device_id = DeviceId
        # self.owner = Owner
        self.topic = topic
        self._on_message = self.on_message
        self._on_update_ready = OnUpdateReady
        self._timer     = None
        self.on_update  = None
        self.interval   = 1
        self.is_running = False
        self.version = _version
        self.date = _date
        
    def on_message(self, client, topic, msg):
        '''Handle the incomming messages
        This function is a virtual function, it should be overriden by the inherriting class '''
        console.debug(f"{topic}:{msg}","Agent.message")

    def Configure(self, mqtt_client):
        '''
        This function is called by the mqtt_client when the agent is added.
        '''
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
    def __init__(self, Host, ClientId=None, Username=None, Password=None, Port=1883):
        self.Agents = {}
        if ( ClientId == None ):
            ClientId =  f"{socket.getfqdn()}.{randint(1,999)}"
        self.ClientId = ClientId
        self.Client = mqtt.Client(self.ClientId)
        self.Host = Host
        self.Port = Port
        self.Topics = []
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
        console.debug(f"Broker ({self.version}_{self.date}) for: {self.ClientId}")
        
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


# use the topics as a list of topics. This will set all the topics to this agent.
    def add(self, agent, topics = None):
        agent.Configure(self.Client)
        if ( topics == None) :
            self.Agents[agent.topic] = agent.on_message
            self.Topics.append(agent.topic)
        else:
            self.Agents['wildcard'] = agent.on_message
            self.Topics = topics

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
            self.Client.subscribe(topic,2)
            console.info(f"Subscribed to: {topic} @ {self.ClientId}" )
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
    