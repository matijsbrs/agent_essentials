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
    """
    Attributes:
        Agents (dict): A dictionary of agents subscribed to topics.
        ClientId (str): The client ID used to connect to the broker.
        Client (mqtt.Client): The MQTT client instance.
        Host (str): The hostname or IP address of the broker.
        Port (int): The port number to connect to.
        Topics (list): A list of topics to subscribe to.
        Subscribed_Topics (list): A list of topics that have been successfully subscribed to.
        Username (str): The username for authentication.
        Password (str): The password for authentication.
        _Thread (Thread): The thread used for running the MQTT client loop.
        version (str): The version of the broker.
        date (str): The date of the broker version.
        _on_message (function): The callback function for handling incoming messages.
        Debug (bool): Flag indicating whether debug mode is enabled.
        Name (str): The name of the broker.

    Methods:
        publish(topic, payload): Publishes a message to the specified topic.
        on_disconnect(): Callback function for handling disconnection from the broker.
        on_connect_fail(): Callback function for handling connection failure to the broker.
        connect() -> bool: Connects to the broker.
        disconnect(): Disconnects from the broker.
        subscribe(topic): Adds a topic to the list of topics to subscribe to.
        _subscribe(topic): Subscribes to the specified topic.
        _unsubscribe(topic): Unsubscribes from the specified topic.
        add(agent): Adds an agent to the broker.
        on_message(client, userdata, msg): Callback function for handling incoming messages.
        on_connect(client, userdata, flags, rc): Callback function for handling successful connection to the broker.
        loop(): Starts the MQTT client loop.
        start(): Starts the broker in a separate thread.
        stop(): Stops the broker and disconnects from the broker.
        join(): Waits for the broker thread to complete.
    """

    def __init__(self, Host, ClientId=None, Username=None, Password=None, Port=1883, Name='NoName'):
        """
        Represents a MQTT broker.

        Args:
            Host (str): The hostname or IP address of the broker.
            ClientId (str, optional): The client ID to use. If not provided, a random client ID will be generated.
            Username (str, optional): The username for authentication.
            Password (str, optional): The password for authentication.
            Port (int, optional): The port number to connect to. Default is 1883.
            Name (str, optional): The name of the broker. Default is 'NoName'.

        """
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
        
    
    def publish(self, payload):
        """
        Publishes the given payload to the broker. using the default topic. (self.topic)

        Args:
            payload: The payload to be published.

        Returns:
            None
        """
        self.Client.publish(self.topic, payload)

    def publish(self, topic, payload):
        """
        Publishes a message to the specified topic.

        Args:
            topic (str): The topic to publish the message to.
            payload (str): The message payload to be published.

        Returns:
            None
        """
        self.Client.publish(topic, payload)
    
    def on_disconnect(self):
        """
        Handles the disconnection from the broker.

        This method is called when the connection to the broker is lost.
        It prints an error message indicating the disconnection and exits the program.

        Parameters:
        None

        Returns:
        None
        """
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
        # ic(topic, self.Subscribed_Topics)
        if topic not in self.Subscribed_Topics:
            # ic(topic, self.Client.subscribe(topic,2))
            state, mid = self.Client.subscribe(topic,2)
            if ( state == 0):
                # console.info(f"Broker:{self.Name} subscribed to: {topic} @ {self.ClientId}")
                self.Subscribed_Topics.append(topic)
            
                # console.error(f"Broker:{self.Name} failed to subscribe to: {topic} @ {self.ClientId}")

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
                #console.notice(f"Broker:{self.Name} subscribing to: {topic} for {agent.eui} @ {self.ClientId}")
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
    