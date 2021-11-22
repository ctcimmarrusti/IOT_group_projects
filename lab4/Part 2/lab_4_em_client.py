# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import *

import time
import json
import pandas as pd
import datetime
import numpy as np
from threading import Lock

#TODO 1: modify the following parameters
#Starting and end index, modify this
device_st = 0
device_end = 5

CO2= [0,0,0,0,0]

#Path to the dataset, modify this
data_path = "data/vehicle{}.csv"

#Path to your certificates, modify this
certificate_formatter = "./certificates/device_{}/cert.pem"
key_formatter = "./certificates/device_{}/private.key"

#https://s3.amazonaws.com/aws-iot-device-sdk-python-docs/sphinx/html/index.html

class MQTTClient:
	def __init__(self, device_id, cert, key):
		print("device_id: ", str(device_id), "\t cert: ", cert, "\t key: ", key )
		# For certificate based connection
		self.device_id = str(device_id)
		self.state = 0
		self.client = AWSIoTMQTTClient(self.device_id)
		#TODO 2: modify your broker address

		self.client.configureEndpoint("a2w4lux87lzneo-ats.iot.us-east-2.amazonaws.com", 8883)
		self.client.configureCredentials("./AmazonRootCA1.pem", key, cert)
		self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
		self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
		self.client.configureConnectDisconnectTimeout(10)  # 10 sec
		self.client.configureMQTTOperationTimeout(5)  # 5 sec
		self.client.onMessage = self.customOnMessage
		# self.client.connect(keepAliveIntervalSecond=10)


	def customOnMessage(self, message):
		#TODO3: fill in the function to show your received message
		print("client {} received -".format(self.device_id), end = " ")

		#Don't delete this line
		# self.client.disconnectAsync()


	# Suback callback
	def customSubackCallback(self, mid, data):
		#You don't need to write anything here
	    pass


	# Puback callback
	def customPubackCallback(self, mid):
		#You don't need to write anything here
	    pass

	def publish(self):
		#TODO4: fill in this function for your publish
		self.client.connect(keepAliveIntervalSecond=10)
		self.client.subscribeAsync("sendCO2", 1, ackCallback=self.customSubackCallback)

		#print("veh" + self.device_id + " " + str(data[int(self.device_id)]["vehicle_CO2"].to_dict()))

		self.client.publishAsync("sendCO2", json.dumps({
			'vehicle_id' : 'veh'+self.device_id,
			'vehicle_CO2' : data[int(self.device_id)]["vehicle_CO2"].to_dict()
		}), 1, ackCallback=self.customPubackCallback)



# Don't change the code below
print("wait")
lock = Lock()
data = []
for i in range(5):
	a = pd.read_csv(data_path.format(i))
	data.append(a)

clients = []
for device_id in range(device_st, device_end):
	client = MQTTClient(device_id,certificate_formatter.format(device_id) ,key_formatter.format(device_id))
	clients.append(client)



states_for_test = [3, 0, 0, 0, 4, 0, 0, 1, 0, 0, 0, 4, 4, 0, 0, 3, 2, 3, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,\
 0, 0, 0, 4, 0, 4, 3, 0, 0, 3, 0, 2, 0, 0, 0, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0,\
  2, 4, 1, 0, 0, 0, 4, 0, 0, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 0, 0, 4, 1, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0,\
   0, 1, 0, 1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 1, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0,\
    0, 0, 4, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 0, 0, 0, 0, 0, 0, 2, 0, 4, 0, 3, 0,\
     0, 4, 1, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0,\
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0, 2,\
       0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 2, 0, 0, 0, 0,\
        0, 1, 2, 1, 0, 0, 4, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 4, 0, 0, 4, 1, 0, 3, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,\
         0, 0, 4, 4, 0, 0, 0, 4, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 1, 2, 0, 0,\
          0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 3, 0, 0, 4, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 4, 0, 0,\
           0, 4, 1, 1, 0, 0, 0, 1, 3, 2, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0,\
            2, 0, 2, 2, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 0, 0, 0, 0, 0, 0, 0, 4]
s1,s2,s3,s4 = [],[],[],[]
for i in range(device_st, device_end):
	if i < 500:
		clients[i].state = states_for_test[i]
		if states_for_test[i] == 1: s1.append(i)
		elif states_for_test[i] == 2: s2.append(i)
		elif states_for_test[i] == 3: s3.append(i)
		elif states_for_test[i] == 4: s4.append(i)


print("Users at state 1: ", s1)
print("Users at state 2: ", s2)
print("Users at state 3: ", s3)
print("Users at state 4: ", s4)



print("send now?")
x = input()
if x == "s":
	for i,c in enumerate(clients):
		c.publish()
elif x == "d":
	for c in clients:
		c.client.disconnect()
		print("All devices disconnected")
else:
	print("wrong key pressed")
