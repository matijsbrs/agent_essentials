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
# @140623_1.3.1 Nieuw minor release. 
#                Added standardizing for telemetry and attributes
# @050224_1.4.0 Major release
#                Refactored the file
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
from agent_essentials.broker import Broker
from agent_essentials.base import _version,_date
from threading import Timer, Thread
import os
from icecream import ic


class Agent:
    broker : Broker = None
    eui = None
    nwid = None
    topic = None # The topic the agent is transmitting by default
    topics = []  # The topics the agent is listening to

    _on_message = None
    timer     = None
    on_update  = None
    interval   = 1
    is_running = False
    version = _version
    date = _date

    # Dictionary with attribute fields.
    # Dictionary with Telemetry fields.
    attributes  = {} 
    telemetry   = {}

    # @050324 ^MBRS Added standardizing Configuration interface.
    Specific_Configuration      = {'Specific'   : False}  # The specific configuration of this device
    Defaults_Configuration      = {'Defaults'   : False}  # The defaults configuration of this device
    Operational_Configuration   = {'Operational': False}  # The operation configuration of this device this 
                                                          #  will be the Merged config from the defaults and 
                                                          #  the specific configuration
    
    system_configuration = None          # Contains the system configuration
    operational_configuration = None     # Contains the operational configuration eg. specific to this device. (mostly derived from the system configuration)

    def __init__(self, broker : Broker =None):
        """
        Initializes an instance of the Agent class.

        Args:
            broker (Broker, optional): The broker object to register the agent with. Defaults to None.
        """
        self.topics = [] # clear the topics
        self.broker = broker
        if self.topic is not None and self.topic not in self.topics:
            self.topics = [self.topic]
        self._on_message = self.on_message
        self._timer = None
        self.on_update = None
        self.interval = 1
        self.is_running = False
        self.version = _version
        self.date = _date
        # self.restore_Attributes()
        if self.broker is not None:
            self.broker.add(self)  # Register the agent with the broker to receive messages
        
    def on_message(self, client, topic, msg):
        '''Handle the incomming messages
        This function is a virtual function, it should be overriden by the inherriting class '''
        console.debug(f"agents.py:on_message {topic}:{msg}","Agent.message")

    def add_Broker(self, broker: Broker):
        self.broker = broker
        self.broker.add(self, self.topic)  # Register the agent with the broker to receive messages
    
    def publish(self, topic, payload):
        if ( self.broker != None):
            self.broker.publish(topic,payload)
        else:
            console.error("agents.py:publish mqtt_client not set. Device offline", self.eui)
 
    def push_payload(self,payloadName = 'attributes', deviceName=None, payload=[]):
        '''
        Push the payload values to the MQTT broker format: self.topic {"payloadName":[{payload}]}
        '''
        if ( deviceName == None ):
            deviceName = self.eui
        if payload == []:
            payload = self.telemetry
        payload = { payloadName: [payload] }
        if ( self.broker is not None ) :
            self.broker.publish(self.topic, json.dumps(payload))


    # Added 050324 ^MBRS standardizing Configuration interface.
    def set_Configuration(self, configuration, defaults=None, system_configuration=None):
        """
        Set the configuration for the agent.

        Args:
            configuration (dict): The specific configuration for the agent.
            defaults (dict, optional): The dfault configuration for the agent. Defaults to None.
            system_configuration (dict, optional): The system configuration for the agent. Defaults to None.

        Returns:
            None
        """
        # First store the defaults to the defaults_configuration
        # Then store the specific configuration to the specific_configuration
        # Then merge the defaults with the specific configuration to the configuration Where the specific configuration overwrites the defaults.
        self.Defaults_Configuration = defaults
        self.Specific_Configuration = configuration
        self.system_configuration = system_configuration
        if self.Defaults_Configuration is not None:
            self.Operational_Configuration = {**defaults, **configuration}
        else:
            self.Operational_Configuration = configuration
       
    def push_configuration(self, configuration=None):
        '''
        Push the configuration values to the MQTT broker format: self.topic {"configuration":[{configuration values}]}
        If configuration == None assume the merged configuration
        '''
        if configuration == []:
            configuration = self.Operational_Configuration
        payload = { 'configuration': [configuration] }
        if ( self.broker is not None ) :
            self.broker.publish(self.topic, json.dumps(payload))

