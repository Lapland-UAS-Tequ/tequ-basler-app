from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from utility import ePrint
import time

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