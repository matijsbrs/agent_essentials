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
	Console.fprint()   Generic fprint with timestamp included.
	Console.Debug()    Debug releated messages. (add source="function name or file")
	Console.Info()     Everything not importand but provides info.
	Console.Warning()  Problems or info that should be handled
	Console.Error()    Display Explicit error messages (critial)
	Console.Notice()   A message received or transmitted eg. operational info

	The output level can be dynamically changed
	See the code for examples

### Agents

An agent links a function call to a topic. When received a given function can be automatically called. 
Also the agent can do  a 'delayed' call. this way a period of data accumulation can take place. 
For example a sensor publishes 10 different values, it can be usefull wait for n seconds before processing the data. 
As it can be that all new values are needed to perform an operation the delayed method makes this possible. 



#### Change Log

Version 1.1.0
	@07122022 ^MB
	Added info_spinner 
	Changed the spinner text layout to [spinner] [text] this look better
	Added option to change the width of the timestamp field
	Added option to change the width of the title field
	Added a notice line. 


Version 1.0.0
	@30112021 ^MB 
	Added documentation and set this as the Version 1.0.0
	Added Version variable to the Agent and Broker. 
 

#### Tips 'n Tricks

Get all git submodules
	'git submodule update --init --recursive'

Install all the required python modules
	$ pip install -r requirements.txt