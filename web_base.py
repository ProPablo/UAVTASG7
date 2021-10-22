from flask import Flask, render_template, Response, send_file
from camera import CamThread, DisplayThread
import cv2
import time
import datetime
import numpy as np
from threading import Thread

app = Flask(__name__)
cam_thread = None

# Worth doing due to cam io
class CamThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.video = cv2.VideoCapture(0)
        success, image = self.video.read()
        self.frame = image
    def run(self):
        while True:
            success, image = self.video.read()
            self.frame = image

class DisplayThread(Thread):
    def __init__(self, cam_thread):
        Thread.__init__(self)
        self.cam_thread = cam_thread
    def run(self):
        while True:
            try:
                cv2.imshow('my webcam', self.cam_thread.frame)
            except:
                pass
            if cv2.waitKey(1) == 27: 
                break  # esc to quit



def gen():
    last_time = datetime.datetime.now()
    frames = 1
    while True:
        frame = cam_thread.frame
        frames+=1
        # diff = time.time() - last_time
        # fps = frames/diff
        
        # compute fps: current_time - last_time
        delta_time = datetime.datetime.now() - last_time
        elapsed_time = delta_time.total_seconds()
        fps = np.around(frames / elapsed_time, 1)
        
        label = f'FPS: {str(fps)}' 
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA) 
        
        ret, jpeg = cv2.imencode('.jpg', frame)
        jpeg = jpeg.tobytes()
        last_time = time.time()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    # This is a single ongoing response that never ends
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    cam_thread = CamThread()
    cam_thread.daemon = True
    cam_thread.start()
    disp = DisplayThread(cam_thread)
    disp.daemon = True
    disp.start()
    app.run(host='0.0.0.0', debug=False)
