from flask import Flask, render_template, Response, send_file
from flask_socketio import SocketIO
# from flask.helpers import send_file
from camera import RecordingCam, VideoCamera, WebVisCamera
import os
import time
import cv2


from flask_socketio import SocketIO, send, emit
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
is_db_created = False
if (os.path.isfile("UAV.db")):
  is_db_created =True

con = sqlite3.connect('UAV.db')

if (not is_db_created):
# Create table
  con.execute('''CREATE TABLE images
                (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, file TEXT)''')

is_recording = False
is_web_vis = False
output_file = "output/cam_video.mp4"
recording_thread = None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recording')
def recording():
    return render_template('recording.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
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
  return Response(gen(WebVisCamera(socket=socketio)),
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


if __name__ == '__main__':
    # clean_output()
    # app.run(host='0.0.0.0', debug=True)
    socketio.run(app, host='0.0.0.0', debug=True)
