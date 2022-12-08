# @081222 ^MB V0.3
#   Reworked to example project based on bridge.tty from the unibridge project
#    - https://github.com/matijsbrs/unibridge (private project)
# @121221 ^MB V0.2
#   added support for environment variables as a step forwards to implement in a docker container
# @101221 ^MB V 0.1 
#   Initial version

# perform a little trick to make this example work.
# the agents_essentials are designed to be used purely as (git) submodule 
# by changing the syspath 
import sys
sys.path.append('../')

import json
import base64
import binascii
from agent_essentials.agents import Broker as Broker
import agent_essentials.console as console
import os
import time
from agent_essentials.Examples import environment_defaults


APP_MAJOR_VERSION = os.environ.get("APP_MAJOR_VERSION")
APP_MINOR_VERSION = os.environ.get("APP_MINOR_VERSION")
APP_BUILD = os.environ.get("APP_BUILD")
APP_VERSION = f"{APP_MAJOR_VERSION}.{APP_MINOR_VERSION}.{APP_BUILD}"

TTN_HOST = os.environ.get("TTN_HOST")
TTN_APPEUI = os.environ.get("TTN_APPEUI")
TTN_APPID = os.environ.get("TTN_APPID")
TTN_TENANTID = os.environ.get("TTN_TENANTID")
TTN_CLIENT_ID = os.environ.get("TTN_CLIENT_ID")
TTN_PASSWORD = os.environ.get("TTN_PASSWORD")

ttn_broker = None
uni_broker = None

def on_connect_mqtt(client, userdata, flags, rc):
    client.subscribe(f"{MQTT_TOPIC_LOCATION}/{MQTT_TOPIC_ORGANISATION}/+/+/tx")
    client.subscribe(f"{MQTT_TOPIC_LOCATION}/{MQTT_TOPIC_ORGANISATION}/+/+/txraw")
    console.info('Connected to Local MQTT')

def on_message_mqtt(client, userdata, msg):
    # extract information from topic
    deveui = msg.topic.split('/')[-3]
    f_port = int(msg.topic.split('/')[-2])
    style = msg.topic.split('/')[-1]
    payload = ''

    # Check the input type
    if style == 'txraw':
        payload = msg.payload.decode('utf-8')
        payload_bytes = bytearray.fromhex(payload)
        base64_bytes = base64.b64encode(payload_bytes)
    elif style == 'tx':
        j_msg = json.loads(msg.payload.decode('utf-8'))
        base64_bytes = j_msg['payload']
    
    # convert payload to BASE64
    base64_message = base64_bytes.decode('ascii')

    # build up structure
    output = {
    "downlinks": [{
        "f_port": f_port,
        "frm_payload": base64_message,
        "confirmed" : False,
        "priority": "NORMAL"
        }]
    }
    
    # convert to json
    payload = json.dumps(output)

    # publish to TTN network
    if TTN_TENANTID != '':
        Username = f"{TTN_APPID}@{TTN_TENANTID}"
    else:
        Username = f"{TTN_APPID}"
    
    console.info(f"v3/{Username}/devices/{deveui}/down/push {payload}")
    ttn_broker.publish(f"v3/{Username}/devices/{deveui}/down/push", payload )



def on_uplink(clinet, topic, msg):
    try:
        deveui = msg['end_device_ids']['dev_eui']
        f_port = msg['uplink_message']['f_port']
    except:
        console.error(f"No dev eui or port found. ignoring frame")
        uni_broker.publish(f"{MQTT_TOPIC_LOCATION}/{MQTT_TOPIC_ORGANISATION}/0000000000000000/00/rx_fail", "")   
        return

    try:
        payload = msg['uplink_message']['frm_payload']
        f_cnt = msg['uplink_message']['f_cnt']
        rssi = msg['uplink_message']['rx_metadata'][0]['rssi']
        snr =  msg['uplink_message']['rx_metadata'][0]['snr']
        time = msg['uplink_message']['received_at']
        dev_addr = msg['end_device_ids']['dev_addr']
    except:
        console.error(f"Uplink frame incomplete")
        uni_broker.publish(f"{MQTT_TOPIC_LOCATION}/{MQTT_TOPIC_ORGANISATION}/{deveui}/{f_port}/rx_fail", "") 
        return   

    frame = {
        "deveui": deveui,
        "devaddr" : dev_addr,
        "time": time,
        "rssi": rssi,
        "snr": snr,
        "payload": payload,
        "port": f_port,
        "f_cnt" : f_cnt
    }

    uni_broker.publish(f"{MQTT_TOPIC_LOCATION}/{MQTT_TOPIC_ORGANISATION}/{deveui}/{f_port}/rxraw", binascii.hexlify(bytearray(base64.b64decode(payload))))
    uni_broker.publish(f"{MQTT_TOPIC_LOCATION}/{MQTT_TOPIC_ORGANISATION}/{deveui}/{f_port}/rx", json.dumps(frame))
    

def on_message(client, userdata, msg):
    j_msg = json.loads(msg.payload.decode('utf-8'))
    console.debug(f"topic: " + msg.topic )

    if msg.topic.split('/')[-1] == 'up':
        on_uplink(client, msg.topic, j_msg)


ttn_broker = Broker(TTN_HOST, TTN_CLIENT_ID, TTN_APPID, TTN_PASSWORD)
ttn_broker.subscribe('#')
ttn_broker._on_message = on_message
ttn_broker.connect()
ttn_broker.start()


try:

    console.info("Bridge started")
    for a in range(3600):
        console.info_spinner("Idle", title="Core")

except KeyboardInterrupt:
    console.notice('disconnect')
    ttn_broker.stop()
    