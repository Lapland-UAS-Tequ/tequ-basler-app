# tequ-basler-app
 Connects to Basler camera and outputs JPEG images to stdout and MJPEG http server. 
 
# Installation 

This installation procedure is for Windows 10 machine. Linux based machines are also supported, but these steps might be different. Please check Basler site for installation steps for Linux.

1. Install Basler pylon software

https://www.baslerweb.com/en/products/software/basler-pylon-camera-software-suite/

2. Install official Basler python wrapper

```
pip install pypylon
```

3. Test your setup with Pylon viewer

4. Install Open

```
pip install opencv-python
```

# Usage





### Sources:

MJPEG server: 
https://github.com/vuquangtrong/pi_streaming 

Basler camera:
https://github.com/basler/pypylon
