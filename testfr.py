import time
last_time = 0
while (True):
  delta = time.time() - last_time
  
  print(delta)
  last_time = time.time()
  time.sleep(0.000000001)