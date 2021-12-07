import socket
import socketserver
import threading


from socket_handler import handler_factory

class CommunicationServer:
    def __init__(self, host_ip, host_port, onMessage):
	    self.host_ip = host_ip
	    self.host_port = host_port 
	    self.onMessage = onMessage
    
    def sendMessage(self, ip, port, message):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(bytes(message + "\n", "utf-8"), (ip, port))

    # Starts a UDP server that doesnt quit until the main program quits
    def start_server(self):
        with socketserver.UDPServer((self.host_ip, self.host_port), handler_factory(self.onMessage)) as server:
            server.serve_forever()
    
    # Start the server on a separate thread        
    def start(self):
        thread = threading.Thread(target=self.start_server)
        thread.start()
        return thread
