import sys


def ePrint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


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
