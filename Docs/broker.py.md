# Broker.py

The `broker.py` file contains the `Broker` class, which serves as a wrapper for the Paho MQTT client. This class simplifies the process of integrating MQTT functionality into your Python applications.

## Class: Broker

The `Broker` class encapsulates the functionality of an MQTT client, providing methods for connecting to a broker, subscribing and unsubscribing from topics, and publishing messages.

### Key Features

- **Simplified Integration**: The `Broker` class abstracts away the complexities of the MQTT protocol, allowing developers to easily integrate MQTT functionality into their applications.

- **Connection Management**: The `Broker` class provides methods for connecting to an MQTT broker, handling connection failures, and managing disconnections.

- **Topic Subscription**: The `Broker` class allows for subscribing to multiple topics and keeps track of the topics it has successfully subscribed to. It also provides the ability to unsubscribe from topics. The received messages will be automatically routed to the Agent on_message method.

- **Message Handling**: The `Broker` class provides a callback method for handling incoming messages from the broker.

### Usage

To use the `Broker` class, you simply need to create an instance of the class, connect to a broker, and then subscribe to the topics you're interested in. The class handles all the details of the MQTT protocol, allowing you to focus on your application logic.

main.py:
> This is a simplified version of [Broker.example.py](../Examples/Broker.example.py)

```python

class System(Agent):

    def __init__(self, broker, base_topic):
        self.topic = f"{base_topic}/system"
        super().__init__(broker=broker)

    def on_message(self, client : Broker, topic, msg):
        # construct an answer
        answer = {'status': 'ok', 'message': 'received'}
        # publish response
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

```

The provided Python code is an example of a simple MQTT (Message Queuing Telemetry Transport) system using a broker and an agent. 

## Broker Class

The `Broker` class represents an MQTT broker. It's responsible for receiving all messages, filtering them, deciding who is interested in them, and then publishing the message to all subscribed clients. The broker is initialized with a host, client ID, username, password, port, and name.

The `Broker` class has several methods, including:

- `publish(topic, payload)`: Publishes a message to a specified topic.
- `connect()`: Connects to the broker.
- `disconnect()`: Disconnects from the broker.
- `subscribe(topic)`: Adds a topic to the list of topics to subscribe to.
- `add(agent)` Adds an agent to the broker.
- `on_message(client, userdata, msg)`: Handles incoming messages.
- `start()` Instruct the broker to start the thread.
- `stop()` Instruct the broker to stop.
- `join()` Wait for the broker thread to exit.

## System Class

The `System` class is a subclass of the `Agent` class. An agent in this context is a client that communicates with the broker. The `System` class is initialized with a broker and a base topic.

The `System` class has the following methods:

- `on_message(client : Broker, topic, msg)`: This method is called when a message is received. It logs the topic and payload of the message, then publishes an acknowledgment message back to the broker.

## Main Function

The main function creates an instance of the `Broker` class and connects to it. It then creates an instance of the `System` class and registers it with the broker. The broker then enters a loop, waiting for messages. If the user interrupts the program (with Ctrl+C), the broker stops, and the program exits.

Here's a simplified flow of the program:

1. The broker is started and begins listening for messages.
2. The system agent is registered with the broker.
3. When a message is received, the broker calls the system agent's `on_message` method.
4. The system agent responds by publishing an acknowledgment message back to the broker.

This code is a basic example of how to set up an MQTT system with a broker and a single agent. In a real-world application, there might be multiple agents, and the `on_message` method could contain more complex logic.
