import argparse
from flask import Flask, render_template, Response, send_file
from flask_socketio import SocketIO
# from flask.helpers import send_file
from camera import RecordingCam, VideoCamera, WebVisCamera


import os
import time
import cv2
import platform

# from gevent import monkey
# monkey.patch_all()
# using socket io with gevent or eventlet stops the server from working once client connects

from flask_socketio import SocketIO, send, emit
import sqlite3
from settings import DB_NAME


is_production = platform.system() == 'Linux'

parser = argparse.ArgumentParser(description="webserver args")
parser.add_argument('--sensor', dest='sensor', action='store_true')
args = parser.parse_args()

if (is_production and args.sensor):
# if (is_production):
    print("using sensor version")
    from sensors import SensorThread, set_diplay_image
else:
    from camera import SensorThread


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=None)

is_db_created = False
if (os.path.isfile("UAV.db")):
    is_db_created = True

con = sqlite3.connect(DB_NAME, check_same_thread=False)


is_recording = False
is_web_vis = False
lcd_mode = 0 # 0= ip, 1= sensor, 2=live_feed
output_file = "output/cam_video.mp4"
recording_thread = None


def init_db():
    # Connect or Create DB File
    images_sql = '''CREATE TABLE IF NOT EXISTS images
                (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, file TEXT)'''
    con.execute(images_sql)

    sensor_sql = """
    CREATE TABLE IF NOT EXISTS 'sensor_data' (
        'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        'timestamp' REAL NOT NULL,
        'temperature' REAL NOT NULL,
        'pressure' REAL NOT NULL,
        'humidity' REAL NOT NULL,
        'light' REAL NOT NULL,
        'gas_reducing' REAL NOT NULL,
        'gas_nh3' REAL NOT NULL,
        'gas_oxidising' REAL NOT NULL);
    """
    con.execute(sensor_sql)


@app.route('/')
def index():
    return render_template('index.html', lcd_mode=lcd_mode)


@app.route('/recording')
def recording():
    return render_template('recording.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        if lcd_mode == 2:
            set_diplay_image(frame)

        ret, jpeg = cv2.imencode('.jpg', frame)
        jpeg = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    # This is a single ongoing response that never ends
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/web_vis_feed')
def web_vis_feed():
    global is_web_vis
    # if (is_web_vis):
    #   return "no can do"
    is_web_vis = True
    return Response(gen(WebVisCamera(socket=socketio, db=con)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/recording_feed')
def recording_feed():
    global is_recording, output_file
    output_file = "output/%d.mp4" % time.time()
    # recording_thread = RecordingCam(output_file)
    # recording_thread.start()
    is_recording = True
    return Response(gen(RecordingCam(filename=output_file)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/stop_recording')
# def stop_recording():
#   global output_file, is_recording
#   global recording_thread
#   recording_thread._stopper.set()
#   recording_thread.join()
#   # os.system('ffmpeg -framerate 10 -pattern_type glob -i "*.jpg" -vf scale=720:-1 -c:v libx264 -pix_fmt yuv420p out.mp4')
#   is_recording = False
#   return "done"


@app.route('/get_recording')
def get_recording():
    global output_file, is_recording
    # os.system('ffmpeg -framerate 10 -pattern_type glob -i "*.jpg" -vf scale=720:-1 -c:v libx264 -pix_fmt yuv420p out.mp4')
    is_recording = False
    time.sleep(0.5)
    return send_file(output_file, as_attachment=True, mimetype="video/mp4")


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)
    emit("event", "connected to server")


@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))


@app.route('/clean_output')
def clean_output():
   # Clean directory
    folder = './output'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
    return 'done'

@app.route('/set_lcd_mode/<int:mode>')
def set_lcd_mode(mode):
    print("changing mode " + str(mode))
    global lcd_mode, s_thread
    lcd_mode = mode
    s_thread.lcd_mode = mode
    return "done"
# def thing():
#   while True:
#     print(time.time())
#     socketio.emit("event", {"time": time.time()})
#     socketio.sleep(0.2)

if __name__ == '__main__':
    # clean_output()
    # app.run(host='0.0.0.0', debug=True)
    # is_production = True
    init_db()

    if (is_production):
        print("On Pi" + str(is_production))

    s_thread = SensorThread(socketio, con)
    # This kills the thread when proc finished otherwise would have to call join()
    s_thread.daemon = True
    s_thread.start()
    # socketio.start_background_task(target=thing)

    socketio.run(app, host='0.0.0.0', debug=not is_production)
