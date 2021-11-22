################################################### Connecting to AWS
import boto3

import json
################################################### Create random name for things
import random
import string
import os

################################################### Parameters for Thing
thingArn = ''
thingId = ''
thingName = ''
defaultPolicyName = 'My_Iot_Policy'
###################################################

def createThing(designator):
	global thingClient
	thingResponse = thingClient.create_thing(
		thingName = thingName
	)
	data = json.loads(json.dumps(thingResponse, sort_keys=False, indent=4))
	for element in data:
		if element == 'thingArn':
			thingArn = data['thingArn']
		elif element == 'thingId':
			thingId = data['thingId']
	createCertificate()

def createCertificate():
	global thingClient
	certResponse = thingClient.create_keys_and_certificate(
			setAsActive = True
	)
	data = json.loads(json.dumps(certResponse, sort_keys=False, indent=4))
	for element in data:
			if element == 'certificateArn':
					certificateArn = data['certificateArn']
			elif element == 'keyPair':
					PublicKey = data['keyPair']['PublicKey']
					PrivateKey = data['keyPair']['PrivateKey']
			elif element == 'certificatePem':
					certificatePem = data['certificatePem']
			elif element == 'certificateId':
					certificateId = data['certificateId']

	os.mkdir("certificates/device_" + thingName)
	with open('certificates/device_'+ thingName + '/public.key', 'w') as outfile:
			outfile.write(PublicKey)
	with open('certificates/device_'+ thingName + '/private.key', 'w') as outfile:
			outfile.write(PrivateKey)
	with open('certificates/device_'+ thingName + '/cert.pem', 'w') as outfile:
			outfile.write(certificatePem)

	response = thingClient.attach_policy(
			policyName = defaultPolicyName,
			target = certificateArn
	)
	response = thingClient.attach_thing_principal(
			thingName = thingName,
			principal = certificateArn
	)

thingClient = boto3.client('iot')
for i in range(0,20):
	thingName = str(i)
	createThing(i)
