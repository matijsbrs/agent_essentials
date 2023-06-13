# Date: 8 juni 2023
# Author: Ing. M. Behrens
# Version: 1.0.0

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
from agent_essentials.agents import Agent, Broker

class Gateway(Agent):

    telemetry_values = [] # {'field name': 'field value'}
    tb_rpc_methods = {}
    tb_attributes = []
    tb_broker : Broker = None

    def __init__(self) -> None:
        console.notice(f"Thingsboard agent ({self.version} @ {self.date})")

    def tb_add_broker(self, broker : Broker):
        self.tb_broker = broker

    def tb_rpc_add(self, name, function):
        rpc = {'name' : name,
               'rpc' : function}
        self.tb_rpc_methods.add(rpc)
    
    def thingsboard_rpc_add(self, name, function):
        self.tb_rpc_methods[name] = function

    def tb_rpc_execute(self, name, param):
        print(f"Execute: {name}")

    def tb_telemetry_push(self, values):
        print("test")

    def tb_push_attributes(self):
        print("te")

    def update_telemetry_value(self, name, value):
        if ( name in self.telemetry_values ):
            self.telemetry_values[name] = value
        else:
            self.telemetry_values.append(name)
            self.telemetry_values[name] = value
        
    def push_telemetry(self,deviceName, values):
        # payload = { deviceName: [ {"values" : values} ]}
        payload = { deviceName: [values] }
        console.info(payload)
        if ( self.tb_broker is not None ) :
            self.tb_broker.publish("v1/gateway/telemetry", json.dumps(payload))


    def dump_telemetry_values(self):
        for field in self.telemetry_values:
            print(f"{field[0]} : {field[1]}")


class Gateway_Agent(Gateway):

    Agent = {}
    topics = []

    def __init__(self) -> None:
        self.topics = [
            'v1/gateway/rpc',
            'v1/gateway/rpc/attributes'
        ]
        self.topic = 'v1/gateway/rpc/request/+'
        console.notice(f"Thingsboard agent ({self.version} @ {self.date})")

    def add_Thingsboard(self, agent, name):
        self.Agent[name] = agent

    def NotifyThingsboard(self):
        for device in self.Agent:
            self.publish('v1/gateway/connect', '{"device":'+device+'}')


    def on_message(self, client, topic, msg):
        # Convert the bytes object to a string
        json_string = msg.payload.decode('utf-8')
        console.notice(f"topic_@: {topic}: {json_string}")
        msgJson = json.loads(json_string)
        console.notice(f"topic_@: {topic}: {msgJson}")
        device = msgJson['device']
        if ( device in self.Agent):
            dev = self.Agent[device]    
            console.notice(f"topic_@: {topic}: for device: {device} Data: {msgJson['data']}")
            if ( topic == "v1/gateway/rpc" ):
                if ( 'method' in msgJson['data'] ):
                    # request
                    request_id = msgJson['data']['id']
                    rpc_ack = {"device": device, "id":request_id, "data": {"success":True}}
                    self.rpc_Device(device, msgJson['data'])
                    client.publish("v1/gateway/rpc", json.dumps(rpc_ack))
                    console.notice(f'pushed ACK {json.dumps(rpc_ack)}')
                elif ( topic == "v1/gateway/rpc/attribute"):
                    self.update_Device_properties(dev , msgJson['data'])
                else:
                    console.notice('ack')
            return
        
        
    def update_Device_properties(self, device, msgData):
    # Iterate over all keys in the msgData dictionary
        for key,value in msgData.items():
            print(f"look for: {key} with value: {value}")
            # Check if this key is a dynamic property of the device
            if key in dir(device):
                # Set the value of the dynamic property to the value in msgData
                setattr(device, key, msgData[key])
                print(f"Key {key} is set to: {value}")

            else:
                # Handle case where key is not a dynamic property
                print(f"Key {key} is not a dynamic property of {device}")

    def rpc_Device(self, device, msgData):
    # Iterate over all keys in the msgData dictionary
        rpc_method = msgData['method']
        for method,function in self.tb_rpc_methods.items():
            if ( rpc_method == method ):
                console.info(f"{device}.rpc method: {method} -> {function(msgData)}")