import picar_4wd as dc
from picar_4wd.speed import Speed
from picar_4wd.utils import cpu_temperature, power_read
import sys
import bluetooth
import threading
import time
import os

# Two commands I have to run when the PI boots up
#os.popen("sudo chmod 777 /var/run/sdp")
#os.popen("sudo hciconfig hci0 piscan")

end_program = False
client_connected = False
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

vehicle_data_changed = True
vehicle_data = {
    "driving_command" : "",
    "direction" : "stopped",
    "speed" : "",
    "total_distance" : "",
    "temperature" : "",
    "battery" : ""
}
def set_vehicle_data(key, value, ignore_flag=False):
    global vehicle_data_changed, vehicle_data
    if not ignore_flag and (not key in vehicle_data or vehicle_data[key] != value):
        vehicle_data_changed = True
    vehicle_data[key] = value

def bt_data_receiver():
    global end_program, client_connected, vehicle_data_changed, vehicle_data

    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]


    bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                                service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                # protocols=[bluetooth.OBEX_UUID]
                                )
        
    print("data_receiver: Advertising server data receiver and waiting for the client's data sender to accept.")

    try:
        client_sock, client_info = server_sock.accept()
    except:
        end_program = True
        server_sock.close()
        print("data_receiver: Faital Excpetion thrown: ", sys.exc_info()[0])
        sys.exit(0)

    print("data_receiver: Client's data sender accepted from", client_info)
    print("data_receiver: You are now listening to the client for driving commands.")

    client_connected = True

    try:
        while not end_program:
            data = client_sock.recv(1024)
            data = data.decode('UTF-8')

            if not data or data == "q":
                end_program = True
                break

            print("Data Received from Client:", data)
            set_vehicle_data("driving_command", data)

    except OSError:
        pass

    print("data_receiver: Disconnected From Client. No longer listening.")

    end_program = True

    client_sock.close()
    server_sock.close()
def bt_data_sender():
    global end_program, client_connected, vehicle_data_changed, vehicle_data

    while not client_connected:
        #print("Client is not connected. Recheck in 2 seconds.")
        time.sleep(2)

    print("data_sender: Searching for client's data receiver.")
    service_matches = bluetooth.find_service(uuid=uuid, address=None)

    if len(service_matches) == 0:
        print("bt_sender: Faital error! Unable to connect with client's data receiver.")
        end_program = True
        sys.exit(0)

    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]        

    print("bt_sender: Connecting to client's data receiver on {}".format(host))

    # Create the client socket
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((host, port))

    print("bt_sender: Connection established to client's data receiver! Ready to send vehicle state information.")

    print("You can both send and recieve data NOW!\n\n")

    while not end_program:
        if vehicle_data_changed:
            sock.send(str(vehicle_data))
            vehicle_data_changed = False
        time.sleep(.1)

    sock.close()
    end_program = True
    print("data_sender: Connection closed. No longer send data.")
def execute_driving_command():
    global end_program, vehicle_data_changed, vehicle_data, client_connected

    current_driving_command = ""

    speedometer = Speed(4)
    # Start spped thread
    speedometer.start()
    total_distance = 0.0

    while not end_program:
        driving_command = vehicle_data['driving_command']
        if current_driving_command != driving_command:
            if driving_command == "w":
                set_vehicle_data("direction", "moving forwards")
                dc.forward(10)
            elif driving_command == "x":
                set_vehicle_data("direction", "moving backwards")
                dc.backward(10)
            elif driving_command == "a":
                set_vehicle_data("direction", "turning left")
                dc.turn_left(10)
            elif driving_command == "d":
                set_vehicle_data("direction", "turning right")
                dc.turn_right(10)
            else:
                set_vehicle_data("direction", "stopped")
                dc.stop()
            current_driving_command = driving_command
        time.sleep(.01)
        speed = speedometer()
        current_distance = round(speed * .01075)
        total_distance += current_distance
        set_vehicle_data("speed", speed)
        set_vehicle_data("total_distance", total_distance)
        set_vehicle_data("temperature", cpu_temperature(), True)
        set_vehicle_data("battery", power_read(), True)
        
    dc.stop()
    print("Driving Program Ended.")

bt_dr = threading.Thread(target=bt_data_receiver)
bt_ds = threading.Thread(target=bt_data_sender)
dr_com = threading.Thread(target=execute_driving_command)

bt_dr.start()
bt_ds.start()
if len(sys.argv) <= 1 or sys.argv[1] != "True":
    dr_com.start()

bt_dr.join()
bt_ds.join()
if len(sys.argv) <= 1 or sys.argv[1] != "True":
    dr_com.join()
