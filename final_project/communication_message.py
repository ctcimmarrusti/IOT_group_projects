import json

class CommunicationMessage:

    def __init__(self, message, destination_ip, path, group_identifier = None):
        self.destination_ip = destination_ip
        self.path = path 
        self.message = message
        self.group_identifier = group_identifier

    def getDestinationIp(self):
        return self.destination_ip

    def getMessage(self):
        return self.message

    def getGroupIdentifier(self):
        return self.group_identifier
    
    def getPath(self):
        return self.path

    def appendToPath(self, ip):
        self.path.append(ip)
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

# When a message is received, can create an object from the json
def loadCommunicationMessageFromJSON(jsonStr):
    communication_message_dict = json.loads(jsonStr)
    communication_message_object = CommunicationMessage(**communication_message_dict)
    return communication_message_object