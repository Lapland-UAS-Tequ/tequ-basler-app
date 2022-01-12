# tequ-basler-app
Connects to Basler camera and outputs JPEG images to stdout and serves JPEG images as MJPEG stream at local http server. This app is tested with Windows 10 machine and with both Basler ACE acA2500-14gm camera (GigE) and Basler Dart daA3840-45uc (USB 3.0). Application is designed to be used as a system command from Node-RED (node-red-node-daemon) but can be used as stand-alone Python app.

Application initializes target Basler camera with parameters configured in special configuration file (Tools -> Save Features), that can be generated with Basler Pylon viewer. Application also uses another configuration file "config.json" to configure for example image post-processing parameters. Application also listens to stdin for commands to be passed to camera in realtime. 

Shutting down application and error handling is not optimized. Application is designed to run forever.
 
## Installation 

This installation procedure is for Windows 10 machine. Linux based machines are also supported, but these steps might be different. Please check Basler site for installation steps for Linux.

### 1. Download and install Basler Pylon software

pylon 6.3.0 Camera Software Suite Windows

https://tequ-files.s3.eu.cloud-object-storage.appdomain.cloud/Basler_pylon_6.3.0.23157.exe

pylon 6.3.0 runtime 

https://tequ-files.s3.eu.cloud-object-storage.appdomain.cloud/pylon_Runtime_6.3.0.23157.exe

### 2. Download and install Python 

https://tequ-win10-nodered-tensorflow.s3.eu.cloud-object-storage.appdomain.cloud/python-3.7.9-amd64.exe

Developed and tested with Python 3.7.9.

### 3. Install official Basler python wrapper
```
pip install pypylon
```

### 4. Test your setup with Pylon viewer

Open Pylon viewer. Search camera from devices list. Connect to camera, test it and configure features. 

Finally Export features file.

Tools -> Save Features.

### 5. Install OpenCV for Python
```
pip install opencv-python
```

Developed and tested with OpenCV 4.5.5.

### 6. Install Node.js and Node-RED

First download and install Node.js.

https://tequ-files.s3.eu.cloud-object-storage.appdomain.cloud/node-v16.13.2-x64.msi

https://nodered.org/docs/getting-started/local

Go to command line and install Node-RED

```
npm install -g --unsafe-perm node-red
```

### 7. Install Node-RED nodes

Install Node-RED nodes that are used in examples flows.

```
npm install node-red-node-daemon
```
```
npm install node-red-contrib-image-output
```
```
npm install node-red-contrib-multipart-stream-decoder
```
```
npm install kevinGodell/node-red-contrib-pipe2jpeg
```

### 8. Clone repository
```
git clone https://github.com/Lapland-UAS-Tequ/tequ-basler-app
```

## Sending commands to application

You can send one or more commands as JSON array to application. 

```
[
   {
      "BalanceWhiteAuto":"Once"
   }
]
```

Send commands as JSON string. 
```
[{"BalanceWhiteAuto":"Once"}]
```
Camera related commands 

(All commands are not supported by both tested camera models and all possible are not implemented.)
```
BalanceWhiteAuto
Height
Width
BinningHorizontal                            
BinningVertical                     
CenterY
ReverseX
ExposureAuto
GainAuto
BlackLevelRaw
GammaEnable
GammaSelector                
PixelFormat                 
ProcessedRawEnable                 
LightSourceSelector                 
AcquisitionFrameRateEnable
AcquisitionFrameRateAbs
AutoTargetValue                          
AutoGainRawLowerLimit
AutoGainRawUpperLimit
AutoExposureTimeAbsLowerLimit        
AutoFunctionProfile
AutoFunctionAOIWidth
AutoFunctionAOIHeight
AutoFunctionAOIOffsetX
AutoFunctionAOIOffsetY
AutoFunctionAOIUsageIntensity
AutoFunctionAOIUsageWhiteBalance
```

Other commands
```
SetDefault
PrintSettings
```                                                  

## Usage in Python

Go to repository path and start app with parameters camera_id and http_port.

```
python main.py <camera_id> <http_port>
```

For example:

```
python main.py 23751808 8081
```

Camera unique identifier can be found using Pylon viewer.

MJPEG stream is available from ```http://localhost:8081/23751808```

# Usage in Node-RED

##  Example 1: Node-RED flow to start app, read images and connect to MJPEG server.

Please modify paths in "Run Basler APP" and "multipart decoder" to match your setup.

![alt text](
https://github.com/Lapland-UAS-Tequ/tequ-basler-app/blob/main/images/example-flow-1.JPG "Example flow")

**Example 1 flow:**
```
[{"id":"7b17aff1d1b99f4e","type":"tab","label":"example","disabled":false,"info":"","env":[]},{"id":"06dc961941923b6c","type":"inject","z":"7b17aff1d1b99f4e","name":"KILL","props":[{"p":"kill","v":"SIGTERM","vt":"str"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"","x":210,"y":80,"wires":[["e92e0f14894ad57b"]]},{"id":"e92e0f14894ad57b","type":"daemon","z":"7b17aff1d1b99f4e","name":"Run Basler APP","command":"C:\\Users\\juha.autioniemi\\AppData\\Local\\Programs\\Python\\Python37\\python.exe ","args":"-u c:\\Users\\juha.autioniemi\\Desktop\\svn\\tequ\\dev\\Python\\apps\\tequ-basler-app\\main.py 23751808 8081","autorun":true,"cr":true,"redo":true,"op":"buffer","closer":"SIGKILL","x":420,"y":80,"wires":[["a5517d277ec0419e"],["7e7cf9de50bd1b23"],[]]},{"id":"d4a81a51ad1d5dea","type":"inject","z":"7b17aff1d1b99f4e","name":"BalanceWhiteAuto","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"","payload":"[{\"BalanceWhiteAuto\":\"Once\"}]","payloadType":"str","x":170,"y":180,"wires":[["e92e0f14894ad57b"]]},{"id":"3df803a8bfa38474","type":"inject","z":"7b17aff1d1b99f4e","name":"PrintSettings","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"","payload":"[{\"PrintSettings\":\"True\"}]","payloadType":"str","x":190,"y":220,"wires":[["e92e0f14894ad57b"]]},{"id":"de01a8f596957e75","type":"image","z":"7b17aff1d1b99f4e","name":"JPEG images","width":"180","data":"payload","dataType":"msg","thumbnail":false,"active":true,"pass":false,"outputs":0,"x":860,"y":60,"wires":[]},{"id":"e1d2405bb471a56e","type":"debug","z":"7b17aff1d1b99f4e","name":"ePrint messages from python app","active":false,"tosidebar":true,"console":false,"tostatus":false,"complete":"true","targetType":"full","statusVal":"","statusType":"auto","x":920,"y":200,"wires":[]},{"id":"7e7cf9de50bd1b23","type":"function","z":"7b17aff1d1b99f4e","name":"fmt","func":"let buf = Buffer.from(msg.payload)\n\nmsg.payload = buf.toString()\n\nif(buf.length > 100000){\n    return null;    \n}\nelse{\n    return msg;       \n}\n","outputs":1,"noerr":0,"initialize":"","finalize":"","libs":[],"x":690,"y":200,"wires":[["e1d2405bb471a56e"]]},{"id":"4bc401fc38f2c3b1","type":"comment","z":"7b17aff1d1b99f4e","name":"Sending commands to stdin","info":"","x":140,"y":140,"wires":[]},{"id":"75486975549580af","type":"comment","z":"7b17aff1d1b99f4e","name":"Connect to MJPEG stream","info":"","x":450,"y":280,"wires":[]},{"id":"3cddc2fa9f92953b","type":"multipart-decoder","z":"7b17aff1d1b99f4e","name":"","ret":"bin","url":"http://localhost:8081/23751808","tls":"","delay":0,"maximum":1000000,"blockSize":1,"x":430,"y":320,"wires":[["a64520dd98f281aa"]]},{"id":"d1f39f5638d4ae28","type":"inject","z":"7b17aff1d1b99f4e","name":"","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"","payload":"","payloadType":"date","x":200,"y":320,"wires":[["3cddc2fa9f92953b"]]},{"id":"a64520dd98f281aa","type":"image","z":"7b17aff1d1b99f4e","name":"JPEG images","width":"180","data":"payload","dataType":"msg","thumbnail":false,"active":true,"pass":false,"outputs":0,"x":860,"y":320,"wires":[]},{"id":"a5517d277ec0419e","type":"pipe2jpeg","z":"7b17aff1d1b99f4e","name":"","x":700,"y":60,"wires":[["de01a8f596957e75"]]}]
```

##  Example 2: Node-RED flow to forward Basler camera image stream to RTSP server.

1. Download, extract to ```c:\rtsp-simple-server``` and start rtsp-simple-server.

https://tequ-files.s3.eu.cloud-object-storage.appdomain.cloud/rtsp-simple-server.7z

2. Download and extract FFmpeg to ```c:\FFmpeg```

https://tequ-files.s3.eu.cloud-object-storage.appdomain.cloud/ffmpeg.7z

3. Setting paths and environmental variables, please check:

https://ffmpeg.org/

4. Install FFmpeg spawn node

```
npm install https://github.com/kevinGodell/node-red-contrib-ffmpeg-spawn
```

5. Please modify paths in "Run Basler APP" and "Run rtsp-simple-server" to match your setup.

6. Access RTSP stream @rtsp://localhost:8554/23751808. You can use for example VLC player.

**Example 1 flow:**

```
[{"id":"06dc961941923b6c","type":"inject","z":"7b17aff1d1b99f4e","name":"KILL","props":[{"p":"kill","v":"SIGTERM","vt":"str"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"","x":230,"y":80,"wires":[["e92e0f14894ad57b"]]},{"id":"e92e0f14894ad57b","type":"daemon","z":"7b17aff1d1b99f4e","name":"Run Basler APP","command":"C:\\Users\\juha.autioniemi\\AppData\\Local\\Programs\\Python\\Python37\\python.exe ","args":"-u c:\\Users\\juha.autioniemi\\Desktop\\svn\\tequ\\dev\\Python\\apps\\tequ-basler-app\\main.py 23751808 8081","autorun":true,"cr":true,"redo":true,"op":"buffer","closer":"SIGKILL","x":420,"y":80,"wires":[["a5517d277ec0419e"],["7e7cf9de50bd1b23"],[]]},{"id":"de01a8f596957e75","type":"image","z":"7b17aff1d1b99f4e","name":"JPEG images","width":"180","data":"payload","dataType":"msg","thumbnail":false,"active":true,"pass":false,"outputs":0,"x":1040,"y":60,"wires":[]},{"id":"e1d2405bb471a56e","type":"debug","z":"7b17aff1d1b99f4e","name":"ePrint messages from python app","active":false,"tosidebar":true,"console":false,"tostatus":false,"complete":"true","targetType":"full","statusVal":"","statusType":"auto","x":1100,"y":200,"wires":[]},{"id":"7e7cf9de50bd1b23","type":"function","z":"7b17aff1d1b99f4e","name":"fmt","func":"let buf = Buffer.from(msg.payload)\n\nmsg.payload = buf.toString()\n\nif(buf.length > 100000){\n    return null;    \n}\nelse{\n    return msg;       \n}\n","outputs":1,"noerr":0,"initialize":"","finalize":"","libs":[],"x":690,"y":120,"wires":[["e1d2405bb471a56e"]]},{"id":"a5517d277ec0419e","type":"pipe2jpeg","z":"7b17aff1d1b99f4e","name":"","x":700,"y":60,"wires":[["de01a8f596957e75","4bf0093a17be8fbe"]]},{"id":"20201d6d5f4221a5","type":"daemon","z":"7b17aff1d1b99f4e","name":"Run rtsp-simple-server","command":"C:\\rtsp-simple-server\\rtsp-simple-server.exe","args":"C:\\rtsp-simple-server\\rtsp-simple-server.yml","autorun":true,"cr":true,"redo":true,"op":"string","closer":"SIGKILL","x":440,"y":280,"wires":[["8e0b4f527c504cd6"],["7fea043ffa87dabd"],["9cb54622f602aca2"]]},{"id":"8e0b4f527c504cd6","type":"debug","z":"7b17aff1d1b99f4e","name":"","active":true,"tosidebar":true,"console":false,"tostatus":false,"complete":"false","statusVal":"","statusType":"auto","x":1030,"y":260,"wires":[]},{"id":"7fea043ffa87dabd","type":"debug","z":"7b17aff1d1b99f4e","name":"","active":true,"tosidebar":true,"console":false,"tostatus":false,"complete":"false","statusVal":"","statusType":"auto","x":1030,"y":300,"wires":[]},{"id":"9cb54622f602aca2","type":"debug","z":"7b17aff1d1b99f4e","name":"","active":true,"tosidebar":true,"console":false,"tostatus":false,"complete":"false","statusVal":"","statusType":"auto","x":1030,"y":340,"wires":[]},{"id":"9ee7766491e1b3f8","type":"inject","z":"7b17aff1d1b99f4e","name":"KILL","props":[{"p":"kill","v":"SIGTERM","vt":"str"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"","x":230,"y":280,"wires":[["20201d6d5f4221a5"]]},{"id":"4bf0093a17be8fbe","type":"ffmpeg-spawn","z":"7b17aff1d1b99f4e","name":"FFmpeg to simple-rtsp-server","outputs":1,"cmdPath":"","cmdArgs":"[]","cmdOutputs":0,"killSignal":"SIGTERM","x":790,"y":400,"wires":[["f44678a02642be3d"]]},{"id":"f44678a02642be3d","type":"debug","z":"7b17aff1d1b99f4e","name":"","active":true,"tosidebar":true,"console":false,"tostatus":false,"complete":"true","targetType":"full","statusVal":"","statusType":"auto","x":1010,"y":400,"wires":[]},{"id":"d1f80f9dd8510826","type":"function","z":"7b17aff1d1b99f4e","name":"Start / restart","func":"let newMsg = {\n  \"action\": {\n    \"command\": msg.topic,\n    \"args\":[\n            \"-i\",\n            \"pipe:0\",\n            \"-tune\",\n            \"zerolatency\",\n            \"-b:v\",\n            \"2M\",\n            \"-maxrate\",\n            \"2M\",\n            \"-bufsize\",\n            \"4M\",\n            \"-f\",\n            \"rtsp\",\n            \"rtsp://localhost:8554/23751808\",\n            \n        ]\n  },\n  \"payload\":msg.payload\n}\n\nreturn newMsg","outputs":1,"noerr":0,"initialize":"","finalize":"","libs":[],"x":410,"y":400,"wires":[["4bf0093a17be8fbe"]]},{"id":"c548123985dc0793","type":"inject","z":"7b17aff1d1b99f4e","name":"start","props":[{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"start","x":230,"y":400,"wires":[["d1f80f9dd8510826"]]},{"id":"98c0564b60cd875c","type":"inject","z":"7b17aff1d1b99f4e","name":"stop","props":[{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"stop","x":230,"y":480,"wires":[["c320b25dc4d439a3"]]},{"id":"17a0260208577abd","type":"inject","z":"7b17aff1d1b99f4e","name":"restart","props":[{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"restart","x":230,"y":440,"wires":[["d1f80f9dd8510826"]]},{"id":"c320b25dc4d439a3","type":"function","z":"7b17aff1d1b99f4e","name":"stop","func":"let newMsg = {\n  \"action\": {\n    \"command\": \"stop\"\n  }\n}\n\nreturn newMsg","outputs":1,"noerr":0,"initialize":"","finalize":"","libs":[],"x":390,"y":480,"wires":[["4bf0093a17be8fbe"]]}]
```



## Links and sources:

Basler

https://github.com/basler/pypylon

OpenCV

https://opencv.org/

Python

https://www.python.org/

Node-RED

https://nodered.org/

Node-RED nodes

https://flows.nodered.org/node/node-red-node-daemon

https://github.com/kevinGodell/node-red-contrib-pipe2jpeg

https://github.com/kevinGodell/node-red-contrib-ffmpeg-spawn

https://flows.nodered.org/node/node-red-contrib-image-output

https://flows.nodered.org/node/node-red-contrib-multipart-stream-decoder


MJPEG server: 

https://github.com/vuquangtrong/pi_streaming 

FFmpeg

https://ffmpeg.org/

rtsp-simple-server

https://github.com/aler9/rtsp-simple-server#installation


