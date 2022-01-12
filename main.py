import io
import json
import os
import sys
from http.server import ThreadingHTTPServer
from mjpegserver import StreamingHandler
from threading import Condition
from threading import Thread
import basler
from utility import ePrint

"""
FrameBuffer is a synchronized buffer which gets each frame and notifies to all waiting clients.
It implements write() method to be used
"""


class FrameBuffer:
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        # New frame
        with self.condition:
            # write to buffer
            self.buffer.seek(0)
            self.buffer.write(buf)
            # crop buffer to exact size
            self.buffer.truncate()
            # save the frame
            self.frame = self.buffer.getvalue()
            # notify all other threads
            self.condition.notify_all()


def main():
    try:
        ePrint(sys.argv)
        camera_id = sys.argv[1]
        port = int(sys.argv[2])
        ePrint("Starting MJPEG Server for camera ID: %s @port %s" % (camera_id, port))
        script_path = os.path.dirname(os.path.realpath(__file__))
        config_path = script_path+'/'+'config.json'

        config_file = open(config_path, "r")
        config = json.load(config_file)
        config_file.close()

        # Create frame_buffer for image data sharing
        frame_buffer = FrameBuffer()

        # Start camera image grabbing
        camera = basler.Basler(config[camera_id], camera_id, frame_buffer)

        # Start camera command handler
        thread1 = Thread(target=camera.cameraCommandHandler)
        thread1.start()

        # Start Datastreamer to StdOut
        if config[camera_id]["converter"]["OutPutToStdOut"]:
            from utility import DataStreamer
            streamer = DataStreamer(frame_buffer)
            thread2 = Thread(target=streamer.writeToStdout)
            thread2.start()

        # Start MJPEG server
        address = ('', port)
        httpd = ThreadingHTTPServer(address, lambda *args: StreamingHandler(frame_buffer, camera_id, *args))
        httpd.serve_forever()
    finally:
        camera.stopGrabbingImages()
        thread1.join()
        if config["converter"]["OutPutToStdOut"]:
            thread2.join()
        ePrint("Threads finished...exiting")
        ePrint("Program finished")


if __name__ == '__main__':
    main()
