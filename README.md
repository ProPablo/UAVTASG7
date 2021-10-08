# UAVTASG7
From https://github.com/pimoroni/enviroplus-python run the installation command

## Process
```
  curl -sSL https://get.pimoroni.com/enviroplus | bash
  pip3 install opencv-python
  sudo apt-get install libcblas-dev
  pip3 install -u numpy
  pip3 install flask-socketio
  

```

# conda
```
conda activate egb
conda install flask
conda install flask-socketio
conda install opencv
conda install numpy
conda install tensorflow
```
<!-- pip3 install eventlet -->

- eventlet is installed to provide a non polling solution (buggy right now, does not allow for page refresh)

- Ensure that the output directory is made and that the perms for it are readable

## Installs
-    Tutorial for object detection using tflite
https://www.digikey.com/en/maker/projects/how-to-perform-object-detection-with-tensorflow-lite-on-raspberry-pi/b929e1519c7c43d5b2c6f89984883588