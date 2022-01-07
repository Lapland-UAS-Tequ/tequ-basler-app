# tequ-basler-app
Connects to Basler camera and outputs JPEG images to stdout and MJPEG http server. This app is tested with Windows 10 machine and Basler ACE acA2500-14gm camera. Application is designed to be used as a system command from Node-RED (node-red-node-daemon) but can be used as stand-alone Python app.
 
# Installation 

This installation procedure is for Windows 10 machine. Linux based machines are also supported, but these steps might be different. Please check Basler site for installation steps for Linux.

1. Install Basler pylon software

https://www.baslerweb.com/en/products/software/basler-pylon-camera-software-suite/

2. Install official Basler python wrapper
```
pip install pypylon
```

3. Test your setup with Pylon viewer

4. Install OpenCV for Python
```
pip install opencv-python
```

5. Install Node-RED

https://nodered.org/docs/getting-started/local

```
npm install -g --unsafe-perm node-red
```

6. Install Node-RED nodes
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


# Usage





### Sources:

Node-RED daemon node
https://flows.nodered.org/node/node-red-node-daemon


MJPEG server: 
https://github.com/vuquangtrong/pi_streaming 

Basler camera:
https://github.com/basler/pypylon
