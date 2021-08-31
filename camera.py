import threading
import cv2
import time
from threading import Thread
face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
ds_factor=0.6

class VideoCamera(object):
    def __init__(self, filename="./output/cam_video.mp4", record=False, images=False):
        self.video = cv2.VideoCapture(0)
        self.images = images
        self.record = record
        
        if (record):
            success, image = self.video.read()
            # image=cv2.resize(image,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
            height, width, channels = image.shape
            # height = 288
            # width = 384
            print("%d %d" % (height, width))
            # vid_cod = cv2.VideoWriter_fourcc(*'XVID')
            vid_cod = cv2.VideoWriter_fourcc(*"XVID")
            fps = 20.0
            # videoWidth = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            # videoHeight = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            # self.output = cv2.VideoWriter("./output/cam_video.avi", vid_cod, fps, (width,height)) 
            self.output = cv2.VideoWriter(filename, vid_cod, fps, (width,height)) 

    
    def __del__(self):
        print("submitting video")
        self.video.release()
        if (self.record):
            self.output.release()
    
    def get_frame(self):
        success, image = self.video.read()
        
        # image=cv2.resize(image,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
        if (self.record):
            self.output.write(image)
            if (self.images):
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
    def __init__(self, filename):
        Thread.__init__(self)
        self._stopper = threading.Event()
        self.video = cv2.VideoCapture(0)
        success, image = self.video.read()
        image=cv2.resize(image,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
        height, width, channels = image.shape
        print("%d %d" % (height, width))
        vid_cod = cv2.VideoWriter_fourcc(*"XVID")
        # fps = 20.0
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.output = cv2.VideoWriter(filename, vid_cod, self.fps, (width,height)) 


    def run(self):
        while not self._stopper.is_set():
            success, image = self.video.read()
            image=cv2.resize(image,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
            self.image = image
            self.output.write(image)
            # time.sleep(0.05) #20 fps
            self._stopper.wait(1/self.fps)
        self.output.release()
    
    def get_frame(self):
        ret, jpeg = cv2.imencode('.jpg', self.image)
        return jpeg.tobytes()

            
        
    

