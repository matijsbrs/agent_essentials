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


class Agent:
    mqtt_client = None
    eui = None
    topic = None
    _on_message = None
    _on_update_ready = None
    timer     = None
    on_update  = None
    interval   = 1
    is_running = False
    version = _version
    date = _date

    # Dictionary with attribute fields.
    # Dictionary with Telemetry fields.
    attributes = {}
    telemetry = {}

    # @050324 ^MBRS Added standardizing Configuration interface.
    Specific_Configuration      = None  # The specific configuration of this device
    Defaults_Configuration      = None  # The defaults configuration of this device
    Operational_Configuration   = None  # The operation configuration of this device this 
                                        # will be the Merged config from the defaults and 
                                        # the specific configuration
    
    # @010324 ^MBRS
    # When set True the pio will try to load external attributes from the json file 
    # located in [external_attribbutes_path]/[eui].attributes.json
    external_attributes = True 
    external_attributes_path = "./pios" 

    def __init__(self) -> None:
        console.notice(f"basic agent ({self.version} @ {self.date})")
        

    def __init__(self, topic, OnUpdateReady , mqtt_client = None, use_external_attributes=True):
        self.mqtt_client = mqtt_client
        self.topic = topic
        self._on_message = self.on_message
        self._on_update_ready = OnUpdateReady
        self._timer     = None
        self.on_update  = None
        self.interval   = 1
        self.is_running = False
        self.version = _version
        self.date = _date
        self.external_attributes = use_external_attributes
        self.Defaults_Configuration = { 'Defaults': False }
        self.Specific_Configuration = { 'Specific': False }
        self.Operational_Configuration = { 'Operational': False }
        self.restore_Attributes()
        
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
        if ( self.mqtt_client != None):
            self.mqtt_client.publish(topic,payload)
        else:
            console.error("mqtt_client not set. Device offline", self.eui)

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

    # Added @140623 ^MBRS standardizing Attribute interface.
    def set_Attribute(self, name, value):
        # set the value of the attribute 
        self.attributes[name] = value

    def get_Attribute(self, name):
        # get the value of the attribute
        if ( name in self.attributes ):
            return self.attributes[name]
        else:
            return {}
        
    def update_Attributes(self, attrList, store=False):
        
        # update the attributes with the new values
        for name, value in attrList.items():
            self.attributes[name] = value      

        if store:
            self.store_Attributes()

    def dump_Attributes(self, startingWith = None):
        # dump the attributes to the console
        for name, value in self.attributes.items():
            if ( startingWith != None ):
                if ( name.startswith(startingWith) ):
                    console.debug(f"{name}:{value}",self.eui) 
            else:
                console.debug(f"{name}:{value}",self.eui) 
    
    def push_Attributes(self,deviceName=None, values=[]):
        '''
        Push the Attribute values to the MQTT broker format: self.topic {"attributes":[{attributes values}]}
        '''
        if ( deviceName == None ):
            deviceName = self.eui
        if values == []:
            values = self.attributes
        payload = { 'attributes': [values] }
        if ( self.mqtt_client is not None ) :
            self.mqtt_client.publish(self.topic, json.dumps(payload))


    def store_Attributes(self, filename=None):
        """
        Store the attributes to a file.

        Args:
            filename (str, optional): The name of the file to store the attributes. If not provided,
                a default filename will be used based on the agent's eui.

        Returns:
            None

        Raises:
            None
        """
        # store the attributes to a file       
        if filename == None:
            if self.eui == None:
                console.error(f"Cannot restore pio without eui.")
                return
            else:
                filename = f"{self.external_attributes_path}/{self.eui}.attributes.json"

        # Create the directory if it does not exist
        if not os.path.exists(self.external_attributes_path):
            os.makedirs(self.external_attributes_path)
            console.notice(f"Directory for external attribute storage: '{self.external_attributes_path}' created successfully.")
        
        try:
            if os.path.exists(filename):
                with open(filename, 'w') as f:  # update existing file
                    f.write(json.dumps(self.attributes))
            else:
                console.notice(f"Creating atrtibute file: {filename}")
                with open(filename, 'x') as f:  # create new file
                    f.write(json.dumps(self.attributes))
        except Exception as ex:
            console.error(f"store_Attributes: {ex}")

    def restore_Attributes(self, filename=None):
        """
        Restores the attributes of the agent from a JSON file.
        When self.external_attributes is set to False, the function will return without doing anything.

        Args:
            filename (str, optional): The path to the JSON file containing the attributes. If not provided,
                the default filename will be used based on the agent's eui.

        Returns:
            None

        Raises:
            None

        """
        if not self.external_attributes:
            return
        
        if filename == None:
            if self.eui == None:
                console.error(f"Cannot restore pio without eui.")
                return
            else:
                filename = f"{self.external_attributes_path}/{self.eui}.attributes.json"

        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:  # reading JSON object
                    self.attributes = json.loads(f.read())
            else:
                console.notice(f"File not found calling store_Attributes: {filename}")
                self.store_Attributes(filename)
        except Exception as ex:
            console.error(f"restore_Attributes failed: {ex}")
            self.store_Attributes(filename)

# Added 050324 ^MBRS standardizing Configuration interface.
    def set_Configuration(self, configuration, defaults=None):
        '''set the  configuration for the pio device.'''
        # First store the defaults to the defaults_configuration
        # Then store the specific configuration to the specific_configuration
        # Then merge the defaults with the specific configuration to the configuration Where the specific configuration overwrites the defaults.
        self.Defaults_Configuration = defaults
        self.Specific_Configuration = configuration
        self.Operational_Configuration = {**defaults, **configuration}
        
# Added @140623 ^MBRS standardizing telemetry interface.
    def set_Telemetry(self, name, value):
        '''
        Set a specific value of a telemetry field
        '''
        self.telemetry[name] = value

    def get_Telemetry(self, name):
        '''
        Get a specific value of a telemetry field
        '''
        if ( name in self.telemetry ):
            return self.telemetry[name]
        else:
            return {}

    def update_telemetry_value(self, name, value):
        '''
        Update a specific value of a telemetry field
        '''
        if ( name in self.telemetry_values ):
            self.telemetry_values[name] = value
        else:
            self.telemetry_values.append(name)
            self.telemetry_values[name] = value

    def update_Telemetries(self, telemetryList):
        '''
        Update the telemetry fields with the new values
        '''
        for name, value in telemetryList.items():
            self.telemetry[name] = value
        
    def push_telemetry(self,deviceName=None, values=[]):
        '''
        Push the telemetry values to the MQTT broker format: self.topic {"telemetry":[{telemetry values}]}
        '''
        if ( deviceName == None ):
            deviceName = self.eui
        if values == []:
            values = self.telemetry
        payload = { 'telemetry': [values] }
        if ( self.mqtt_client is not None ) :
            self.mqtt_client.publish(self.topic, json.dumps(payload))

    def dump_telemetry_values(self):
        '''
        Debug function to dump the telemetry values to the console
        '''
        for field in self.telemetry_values:
            print(f"{field[0]} : {field[1]}")

    def push_configuration(self, configuration=None):
        '''
        Push the configuration values to the MQTT broker format: self.topic {"configuration":[{configuration values}]}
        If configuration == None assume the merged configuration
        '''
        if configuration == []:
            configuration = self.Operational_Configuration
        payload = { 'configuration': [configuration] }
        if ( self.mqtt_client is not None ) :
            self.mqtt_client.publish(self.topic, json.dumps(payload))

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
    