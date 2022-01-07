import basler
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Condition
import time
import io
from threading import Thread
import os
import sys
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
        if buf.startswith(b'\xff\xd8'):
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
                # print(self.buffer.getbuffer().nbytes)


'''
StreamingHandler extent http.server.SimpleHTTPRequestHandler class to handle mjpg file for live stream
'''


class StreamingHandler(SimpleHTTPRequestHandler):
    def __init__(self, frames_buffer, camera_id, *args):
        self.frames_buffer = frames_buffer
        self.camera_id = camera_id
        ePrint("New StreamingHandler, using frames_buffer=", frames_buffer)
        super().__init__(*args)

    def __del__(self):
        ePrint("Remove StreamingHandler")

    def do_GET(self):
        if self.path == '/'+self.camera_id:
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                # tracking serving time
                start_time = time.time()
                frame_count = 0
                # endless stream
                while True:
                    with self.frames_buffer.condition:
                        # wait for a new frame
                        self.frames_buffer.condition.wait()
                        # it's available, pick it up
                        frame = self.frames_buffer.frame
                        # send it
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', len(frame))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
                        # count frames
                        frame_count += 1
                        # calculate FPS every 5s
                        if (time.time() - start_time) > 5:
                            ePrint("MJPEG stream FPS: %.1f" % (float(frame_count) / (time.time() - start_time)))
                            frame_count = 0
                            start_time = time.time()
            except Exception as e:
                ePrint(f'Removed streaming client {self.client_address}, {str(e)}')
        else:
            # fallback to default handler
            super().do_GET()


'''
DataStreamer writes JPEG frames to stdout
'''


class DataStreamer:
    def __init__(self, frame_buffer):
        self.frame_buffer = frame_buffer
        ePrint("DataStreamer created")

    def writeToStdout(self):
        while True:
            try:
                with self.frame_buffer.condition:
                    # wait for a new frame
                    self.frame_buffer.condition.wait()
                    # it's available, pick it up
                    frame = self.frame_buffer.frame
                    # send it to stdout
                    sys.stdout.buffer.write(frame)
            except:
                pass


def main():
    try:
        ePrint(sys.argv)
        camera_id = sys.argv[1]
        port = int(sys.argv[2])
        ePrint("Starting MJPEG Server for camera ID: %s @port %s" % (camera_id, port))
        script_path = os.path.dirname(os.path.realpath(__file__))
        config_file = open(script_path+'/'+'config.json', "r")
        config = json.load(config_file)
        config_file.close()

        frame_buffer = FrameBuffer()
        camera = basler.Basler(config[camera_id], camera_id, frame_buffer)
        streamer = DataStreamer(frame_buffer)

        thread1 = Thread(target=camera.cameraCommandHandler)
        thread1.start()

        thread2 = Thread(target=streamer.writeToStdout)
        thread2.start()
        ePrint("Threads started")

        address = ('', port)
        httpd = ThreadingHTTPServer(address, lambda *args: StreamingHandler(frame_buffer, camera_id, *args))
        httpd.serve_forever()
    finally:
        camera.stopGrabbingImages()
        thread1.join()
        thread2.join()
        ePrint("Threads finished...exiting")
        ePrint("Program finished")


if __name__ == '__main__':
    main()
