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
<!-- pip3 install eventlet -->

- eventlet is installed to provide a non polling solution (buggy right now, does not allow for page refresh)

- Ensure that the output directory is made and that the perms for it are readable