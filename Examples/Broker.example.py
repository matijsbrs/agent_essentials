# use import sys to add the path to the agent_essentials library.
# so the example can run from 
import sys
sys.path.append('../../')

from agent_essentials.agents import Agent, Broker
from icecream import ic
import json


class System(Agent):

    def __init__(self, broker, base_topic):
        self.topic = f"{base_topic}/system"
        self.use_external_attributes = False # This is a system interface, it does not use external attributes
        super().__init__(broker=broker)

    def on_message(self, client : Broker, topic, msg):
        ic(topic, msg.payload)
        answer = {'status': 'ok', 'message': 'received'}
        client.publish(f"{topic}/answer", json.dumps(answer))


if __name__ == '__main__':

    broker = Broker('localhost',Name="DemoBroker")
    broker.connect()
    broker.start()
    
    system = System(broker, "server/agent")

    try:
        print("Press Ctrl+C to stop")
        broker.join()
    except KeyboardInterrupt:
        broker.stop()
    
    print("Exiting")
    exit(0)
