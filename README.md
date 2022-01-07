# tequ-basler-app
Connects to Basler camera and outputs JPEG images to stdout and serves JPEG images as MJPEG stream at local http server. This app is tested with Windows 10 machine and Basler ACE acA2500-14gm camera. Application is designed to be used as a system command from Node-RED (node-red-node-daemon) but can be used as stand-alone Python app.

Application initializes target Basler camera with parameters configured in config.json. Application also listens to stdin for commands to be passed to camera in realtime. 

Shutting down application and error handling is not optimized. Application is designed to run forever.
 
## Installation 

This installation procedure is for Windows 10 machine. Linux based machines are also supported, but these steps might be different. Please check Basler site for installation steps for Linux.

### 1. Install Basler pylon software

https://www.baslerweb.com/en/products/software/basler-pylon-camera-software-suite/

### 2. Install Python 

Developed and tested with Python 3.7.9.

### 3. Install official Basler python wrapper
```
pip install pypylon
```

### 4. Test your setup with Pylon viewer

### 5. Install OpenCV for Python
```
pip install opencv-python
```

Developed and tested with OpenCV 4.5.5.

### 6. Install Node-RED

https://nodered.org/docs/getting-started/local

```
npm install -g --unsafe-perm node-red
```

### 7. Install Node-RED nodes
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

MJPEG stream is available from http://localhost:8081/23751808

## Usage in Node-RED

Please modify paths in node-red-node-daemon node and multipart-decoder to match your setup.

![alt text](
https://github.com/Lapland-UAS-Tequ/tequ-basler-app/blob/main/images/example-flow.JPG "Example flow")

Example flow:
```
[{"id":"06dc961941923b6c","type":"inject","z":"7b17aff1d1b99f4e","name":"KILL","props":[{"p":"kill","v":"SIGTERM","vt":"str"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"","x":210,"y":100,"wires":[["e92e0f14894ad57b"]]},{"id":"e92e0f14894ad57b","type":"daemon","z":"7b17aff1d1b99f4e","name":"Run Basler APP","command":"C:\\Users\\juha.autioniemi\\AppData\\Local\\Programs\\Python\\Python37\\python.exe ","args":"-u c:\\Users\\juha.autioniemi\\Desktop\\svn\\tequ\\dev\\Python\\apps\\tequ-basler-app\\main.py 23751808 8081","autorun":true,"cr":true,"redo":true,"op":"buffer","closer":"SIGKILL","x":420,"y":100,"wires":[["de01a8f596957e75"],["7e7cf9de50bd1b23"],[]]},{"id":"d4a81a51ad1d5dea","type":"inject","z":"7b17aff1d1b99f4e","name":"BalanceWhiteAuto","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"","payload":"[{\"BalanceWhiteAuto\":\"Once\"}]","payloadType":"str","x":170,"y":200,"wires":[["e92e0f14894ad57b"]]},{"id":"3df803a8bfa38474","type":"inject","z":"7b17aff1d1b99f4e","name":"PrintSettings","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"","payload":"[{\"PrintSettings\":\"True\"}]","payloadType":"str","x":190,"y":240,"wires":[["e92e0f14894ad57b"]]},{"id":"de01a8f596957e75","type":"image","z":"7b17aff1d1b99f4e","name":"JPEG images","width":"480","data":"payload","dataType":"msg","thumbnail":false,"active":true,"pass":false,"outputs":0,"x":720,"y":80,"wires":[]},{"id":"e1d2405bb471a56e","type":"debug","z":"7b17aff1d1b99f4e","name":"ePrint messages from python app","active":false,"tosidebar":true,"console":false,"tostatus":false,"complete":"true","targetType":"full","statusVal":"","statusType":"auto","x":920,"y":340,"wires":[]},{"id":"7e7cf9de50bd1b23","type":"function","z":"7b17aff1d1b99f4e","name":"fmt","func":"let buf = Buffer.from(msg.payload)\n\nmsg.payload = buf.toString()\n\nif(buf.length > 100000){\n    return null;    \n}\nelse{\n    return msg;       \n}\n","outputs":1,"noerr":0,"initialize":"","finalize":"","libs":[],"x":690,"y":340,"wires":[["e1d2405bb471a56e"]]},{"id":"4bc401fc38f2c3b1","type":"comment","z":"7b17aff1d1b99f4e","name":"Sending commands to stdin","info":"","x":140,"y":160,"wires":[]},{"id":"75486975549580af","type":"comment","z":"7b17aff1d1b99f4e","name":"Connect to MJPEG stream","info":"","x":450,"y":380,"wires":[]},{"id":"3cddc2fa9f92953b","type":"multipart-decoder","z":"7b17aff1d1b99f4e","name":"","ret":"bin","url":"http://localhost:8081/23751808","tls":"","delay":0,"maximum":1000000,"blockSize":1,"x":430,"y":420,"wires":[["a64520dd98f281aa"]]},{"id":"d1f39f5638d4ae28","type":"inject","z":"7b17aff1d1b99f4e","name":"","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"","payload":"","payloadType":"date","x":230,"y":420,"wires":[["3cddc2fa9f92953b"]]},{"id":"a64520dd98f281aa","type":"image","z":"7b17aff1d1b99f4e","name":"JPEG images","width":"480","data":"payload","dataType":"msg","thumbnail":false,"active":true,"pass":false,"outputs":0,"x":720,"y":420,"wires":[]}]
```

## Sources:

Node-RED daemon node
https://flows.nodered.org/node/node-red-node-daemon

MJPEG server: 
https://github.com/vuquangtrong/pi_streaming 

Basler camera:
https://github.com/basler/pypylon
