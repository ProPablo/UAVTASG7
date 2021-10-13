import threading
import cv2
import time
from threading import Thread
from flask_socketio import SocketIO
from sqlite3 import Connection, connect
import numpy as np
from objdetect_funcs import compute_recognition
from arucodetect_funcs import aruco_detect
import random
from settings import DB_NAME
import sqlite3


face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
ds_factor = 0.6


class VideoCamera(object):
    def __init__(self, ):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        print("killing video")
        self.video.release()

    def get_frame(self) -> np.ndarray:
        success, image = self.video.read()
        image = cv2.resize(image, None, fx=ds_factor,
                           fy=ds_factor, interpolation=cv2.INTER_AREA)
        return image


class WebVisCamera(VideoCamera):
    def __init__(self, socket: SocketIO, db, image_interval=5):
        self.socket = socket
        self.db_con = db
        # self.db_con = connect(DB_NAME)
        self.last_time = 0
        self.image_interval = image_interval
        super().__init__()

    def get_frame(self) -> np.ndarray:
        image = super().get_frame()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image, obj_info = compute_recognition(image)
        obj_info = []
        image, aruco_info = aruco_detect(image)
        # face_rects = face_cascade.detectMultiScale(gray, 1.3, 5)
        # for (x, y, w, h) in face_rects:
        #     cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        #     break
        

        if (time.time() - self.last_time > self.image_interval):
            # print("got stuff" + stuff)

            file_path = "output/%d.jpg" % time.time()
            # Writing to file is the clear bottleneck here therefore,
            # threading isnt going to solve that unless we use some kind of threadpool to acually save to disk
            cv2.imwrite(file_path, image)
            # without the trailing comma the param is evaluated as input sequence not tuple
            self.db_con.execute(
                "INSERT into images(file) values(?)", (file_path,))
            self.db_con.commit()
            self.socket.emit("img", file_path, broadcast=True)
            self.socket.emit("img_process", {"aruco": aruco_info, "obj": obj_info})
            self.last_time = time.time()

        return image


class RecordingCam(VideoCamera):
    def __init__(self, filename="output/cam_video.mp4"):
        super().__init__()
        self.filename = filename
        success, image = self.video.read()
        image = cv2.resize(image, None, fx=ds_factor,
                           fy=ds_factor, interpolation=cv2.INTER_AREA)
        height, width, channels = image.shape
        print("%d %d" % (height, width))
        vid_cod = cv2.VideoWriter_fourcc(*"XVID")
        fps = 20.0
        # videoWidth = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        # videoHeight = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.output = cv2.VideoWriter(filename, vid_cod, fps, (width, height))

    def get_frame(self):
        image = super().get_frame()
        self.output.write(image)
        return image

    def __del__(self):
        self.output.release()
        return super().__del__()


class RecordingThread(Thread):
    def __init__(self, filename):
        Thread.__init__(self)
        self._stopper = threading.Event()
        self.video = cv2.VideoCapture(0)
        success, image = self.video.read()
        image = cv2.resize(image, None, fx=ds_factor,
                           fy=ds_factor, interpolation=cv2.INTER_AREA)
        height, width, channels = image.shape
        print("%d %d" % (height, width))
        vid_cod = cv2.VideoWriter_fourcc(*"XVID")
        # fps = 20.0
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.output = cv2.VideoWriter(
            filename, vid_cod, self.fps, (width, height))

    def run(self):
        while not self._stopper.is_set():
            success, image = self.video.read()
            image = cv2.resize(image, None, fx=ds_factor,
                               fy=ds_factor, interpolation=cv2.INTER_AREA)
            self.image = image
            self.output.write(image)
            # time.sleep(0.05) #20 fps
            self._stopper.wait(1/self.fps)
        self.output.release()

    def get_frame(self):
        ret, jpeg = cv2.imencode('.jpg', self.image)
        return jpeg.tobytes()


class SensorThread(Thread):
    def __init__(self, socket: SocketIO, interval=5):
        Thread.__init__(self)
        self.counter = 0
        self.socket = socket
        self.interval = interval

    def run(self):
        self.db_conn = sqlite3.connect(DB_NAME)
        while True:
            self.counter += 1
            print(self.db_conn.execute("SELECT count(*) FROM images"))
            # print(self.counter)
            # this blocks other threads completely
            sql = """INSERT INTO Sensor_Data(timestamp) values(?)"""
            self.db_conn.execute(sql, (time.time(),))
            self.socket.emit(
                "sensor", {"time": time.time()*1e3, "counter": self.counter, "data": random.random()})
            time.sleep(self.interval)
