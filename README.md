# agent_essentials
Essentials for programming agents
	
## Components:

* MQTT Broker Wrapper
* Console beautifier
* Agents 

### MQTT Broker Wrapper

The Broker wrapper handles the connecting of agents to a given MQTT broker.


### Console beautifier

Wrapper functions for console output

Features:
	Console.fprint()
	Console.Debug()
	Console.Info()
	Console.Warning()
	Console.Error()

	The output level can be dynamically changed
	See the code for examples

### Agents

An agent links a function call to a topic. When received a given function can be automatically called. 
Also the agent can do  a 'delayed' call. this way a period of data accumulation can take place. 
For example a sensor publishes 10 different values, it can be usefull wait for n seconds before processing the data. 
As it can be that all new values are needed to perform an operation the delayed method makes this possible. 



#### Change Log

Version 1.0.0
	@30112021 ^MB 
	Added documentation and set this as the Version 1.0.0
 
