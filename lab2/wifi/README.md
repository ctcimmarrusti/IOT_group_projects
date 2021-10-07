## Copy source to both Pi and PC

And then: 

## For Pi
Open the file `/pi/Pi_Server/wifi_server.py` and change the IP address at the top to the IP address of the Pi on your local network

run `python3 /pi/Pi_Server/wifi_server.py`

## For PC
Navigate to /client/electron in a terminal

run `npm install`

Edit file `index.js` and update the IP at the top to the IP of the Pi Host

run `npm start`


