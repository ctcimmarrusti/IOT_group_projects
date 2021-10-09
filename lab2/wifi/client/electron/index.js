document.onkeydown = updateKey;
document.onkeyup = resetKey;

var server_port_camera = 65433;
var server_port_command = 65432;
var server_port_stats = 65434;

var server_addr = "192.168.2.107";   // the IP address of your Raspberry PI
var commandclient = null;


function cameraclientinit() {
    const net = require('net');
    const client = net.createConnection({ port: server_port_camera, host: server_addr }, () => {
        console.log('connected to camera pipe!');
    });
    let imagedata = '';
    client.on('data', (data) => {
        try {
            const chunk = data.toString();
            chunkSplits = chunk.split('\r\n');
            if (chunkSplits.length === 1) {
                imagedata += chunkSplits[0];
            } else {
                imagedata += chunkSplits[0];
                document.getElementById("imageholder").src = `data:image/jpeg;base64,${imagedata}`;
                imagedata = chunkSplits[1];
            }
        }
        catch (err) {
            console.log(err);
        }
    });
    client.on('end', () => {
        console.log('disconnected from server');
    });
}
function statsclientinit() {
    const net = require('net');
    const client = net.createConnection({ port: server_port_stats, host: server_addr }, () => {
        console.log('connected to stats pipe!');
    });
    let statsdata = '';
    client.on('data', (data) => {
        try {
            const chunk = data.toString();
            chunkSplits = chunk.split('\r\n');
            if (chunkSplits.length === 1) {
                statsdata += chunkSplits[0];
            } else {
                statsdata += chunkSplits[0];
                statsJSON = JSON.parse(statsdata);
                //document.getElementById("stats").innerHTML = `CPU Temp: ${statsJSON.cputemp}  <br/>   GPU Temp: ${statsJSON.gputemp}   <br/>  Battery: ${statsJSON.battery}`;
                document.getElementById("cpu-t").innerText = statsJSON.cputemp;
                document.getElementById("gpu-t").innerText = statsJSON.gputemp;
                document.getElementById("battery").innerText = statsJSON.battery;
                statsdata = chunkSplits[chunkSplits.length -1];
            }
        }
        catch (err) {
            console.log(err);
        }
    });
    client.on('end', () => {
        console.log('disconnected from server');
    });
}
function commandclientinit() {
    const net = require('net');
    commandclient = net.createConnection({ port: server_port_command, host: server_addr }, () => {
        console.log('connected to command pipe!');
    });

    commandclient.on('end', () => {
        console.log('disconnected from server');
    });
}
let lastKey = ['', Date.now()]

function updateKey(e) {
    e = e || window.event;

    if (e.keyCode == '87') {
        // up (w)
        document.getElementById("upArrow").style.color = "green";
        lastKey = ['87', Date.now()]
    }
    else if (e.keyCode == '83') {
        // down (s)
        document.getElementById("downArrow").style.color = "green";
        lastKey = ['83', Date.now()]
    }
    else if (e.keyCode == '65') {
        // left (a)
        document.getElementById("leftArrow").style.color = "green";
        lastKey = ['65', Date.now()]
    }
    else if (e.keyCode == '68') {
        // right (d)
        document.getElementById("rightArrow").style.color = "green";
        lastKey = ['68', Date.now()]
    }
}
// reset the key to the start state 
function resetKey(e) {

    e = e || window.event;

    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";
}
const updateCommandClient = () => {
    
    if (Date.now() - lastKey[1] <  500) {
        commandclient && commandclient.write(lastKey[0])
    }
    else {
        commandclient && commandclient.write('STOP')
    }
}
function initiate() {
    commandclientinit();
    statsclientinit();
    cameraclientinit();
    setInterval(function () {
        updateCommandClient();
    }, 25);
}
