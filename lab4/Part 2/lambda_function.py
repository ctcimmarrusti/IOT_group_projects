import json
import boto3
import time
from decimal import *

def lambda_handler(event, context):
    # TODO implement
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('max_co2_table')
    
    vehicle_id = event['vehicle_id']
    # https://stackoverflow.com/questions/28425117/dynamodbnumbererror-on-trying-to-insert-floating-point-number-using-python-boto
    vehicle_CO2 = json.loads(json.dumps(event['vehicle_CO2']), parse_float=Decimal)
    
    maxCO2 = 0
    for i, (j,k) in enumerate(vehicle_CO2.items()):
        maxCO2 = max(k, maxCO2);
    
    record = {
        'timestamp': int(time.time()),
        'vehicle_id' : vehicle_id,
        'maxCO2' : maxCO2
        #'vehicle_CO2' : vehicle_CO2,
        #'event' : json.dumps(event)
    }
    
    table.put_item(Item=record)
    
    return {
        'statusCode': 200,
        'body' : "Max CO2 is " + str(maxCO2)
        #'body' : json.dumps(record),
        #'data_str' : event['data']
        #'newMax' : max(m, r)
    }
