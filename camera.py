import cv2
import time
from threading import Thread
face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
ds_factor=0.6

class VideoCamera(object):
    def __init__(self, record=False):
        self.video = cv2.VideoCapture(0)
        self.record = record
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        image=cv2.resize(image,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
        if (self.record):
            file_path = "./output/%d.jpg" % time.time()
            # Writing to file is the clear bottleneck here therefore, 
            # threading isnt going to solve that unless we use some kind of threadpool to acually save to disk
            cv2.imwrite(file_path, image)
        else:
            gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            face_rects=face_cascade.detectMultiScale(gray,1.3,5)
            for (x,y,w,h) in face_rects:
                cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
                break

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

class RecordingCam(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._stop = False
        self.video = cv2.VideoCapture(0)

    def run(self):
      while not self._stop:
        success, image = self.video.read()
        file_path = "./output/%d.jpg" % time.time()
        cv2.imwrite(file_path, image)

