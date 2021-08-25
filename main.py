from flask import Flask, render_template, Response, send_file
# from flask.helpers import send_file
from camera import VideoCamera, RecordingCam
import os
import time

import zipfile
import io

app = Flask(__name__)
is_recording = False
output_file = "./output/cam_video.mp4"


@app.route('/clean_output')
def clean_output():
   # Clean directory
  folder = './output'
  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recording')
def recording():
    return render_template('recording.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    # This is a single ongoing response that never ends
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_recording')
def start_recording():
  global is_recording, output_file
  if (is_recording):
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame') 
  else:
  # global recording_thread
  # recording_thread = RecordingCam()
    # recording_thread.start()
    is_recording = True
    output_file = "./output/%d.mp4" % time.time()
    return Response(gen(VideoCamera(record=True, filename=output_file)),
                      mimetype='multipart/x-mixed-replace; boundary=frame')  

@app.route('/stop_recording')
def stop_recording():
  global output_file, is_recording
  # global recording_thread
  # recording_thread._stop = True
  # recording_thread.join()
  # os.system('ffmpeg -framerate 10 -pattern_type glob -i "*.jpg" -vf scale=720:-1 -c:v libx264 -pix_fmt yuv420p out.mp4')
  # clean_output()
  is_recording = False
  # time.sleep(0.5)
  return "done"
  # return send_file(output_file, as_attachment=True, mimetype="video/mp4")

@app.route('/get_recording')
def get_recording():
  global output_file, is_recording
  # global recording_thread
  # recording_thread._stop = True
  # recording_thread.join()
  # os.system('ffmpeg -framerate 10 -pattern_type glob -i "*.jpg" -vf scale=720:-1 -c:v libx264 -pix_fmt yuv420p out.mp4')
  # clean_output()
  is_recording = False
  time.sleep(0.5)
  return send_file(output_file, as_attachment=True, mimetype="video/mp4")

if __name__ == '__main__':
    # clean_output()
    app.run(host='0.0.0.0', debug=True)
