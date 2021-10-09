import sys
import bluetooth
import threading
import time

server_connected = False
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
end_program = False

def bt_data_receiver():
    global end_program, server_connected

    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                                service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                # protocols=[bluetooth.OBEX_UUID]
                                )

    print("data_receiver: Advertising client data receiver and waiting for the server's data sender to accept.")

    try:
        client_sock, client_info = server_sock.accept()
    except:
        end_program = True
        server_sock.close()
        print("data_receiver: Faital Excpetion thrown: ", sys.exc_info()[0])
        sys.exit(0)

    print("data_receiver: Server's data sender accepted from", client_info)
    print("data_receiver: You are now listening to the server for vehicle state information.")

    server_connected = True

    try:
        while not end_program:
            data = client_sock.recv(1024)
            data = data.decode('UTF-8')

            if not data or data == "q":
                end_program = True
                break

            print("Data Received from Server:", data)
            
    except OSError:
        pass

    end_program = True

    print("data_receiver: Disconnected From Server. No longer listening.")

    client_sock.close()
    server_sock.close()
def bt_data_sender():
    global end_program, server_connected

    print("data_sender: Searching for server's data receiver.")
    service_matches = bluetooth.find_service(uuid=uuid, address=None)

    if len(service_matches) == 0:
        print("bt_sender: Faital error! Unable to connect with server's data receiver.")
        end_program = True
        sys.exit(0)

    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]        

    print("bt_sender: Connecting to server's data receiver on {} using port {}".format(host, port))

    # Create the client socket
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        sock.connect((host, port))
    except:
        print("bt_sender: failed, trying again.")
        sock.connect((host, port))

    print("bt_sender: Connection established to server's data receiver! Ready to send driving commands.")

    while not server_connected:
        #print("Server is not connected. Rechecking in 2 seconds.")
        time.sleep(2)
    
    print("You can both send and recieve data NOW!\n\n")

    print("Enter driving commands (w=forward, x=backward, a=left, d=right, s=stop, =quit):")

    while not end_program:
        data = input()
        if not data:
            end_program = True
            break
        sock.send(data)

    sock.close()
    end_program = True
    print("data_sender: Connection closed. No longer send data.")

sth = threading.Thread(target=bt_data_receiver)
cth = threading.Thread(target=bt_data_sender)

sth.start()
cth.start()

cth.join()
sth.join()
