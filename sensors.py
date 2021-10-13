from threading import Thread
import time
from flask_socketio import SocketIO
import logging
import ST7735 # LCD
from bme280 import BME280 # Temperature, Humidity, Pressure
from enviroplus import gas
from enviroplus.noise import Noise

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont

import sys
import socket
import numpy as np
import sqlite3
from settings import DB_NAME

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus    

noise = Noise()

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""light.py - Print readings from the LTR559 Light & Proximity sensor and  BME280.

Press Ctrl+C to exit!

""")

# Create ST7735 LCD display class
st7735 = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)
# Initialize display
st7735.begin()
WIDTH = st7735.width
HEIGHT = st7735.height

# Set up canvas and font
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
font_size = 12
font = ImageFont.truetype(UserFont, font_size)

message = ""

# The position of the top bar
top_pos = 25

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

# Is this needed
gas.enable_adc()
#as.set_adc_gain(4.096)s

def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
        print(temp)
    return temp

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def set_diplay_image(img):
    #convert to PIL
    im_pil = Image.fromarray(img)
    im_pil = im_pil.resize((WIDTH, HEIGHT))
    st7735.display(im_pil)

# EDIT: User can choose IP, Temp or Image Display
# Displays data and text on the 0.96" LCD
def display_text(variable, data, unit):

    #Obtain the CPU temperature
    cpu_temp = get_cpu_temperature()
    cpu_message = "CPU Temp: %s C" % cpu_temp
    # Format the variable name and value
    message = "{}: {:.1f} {}".format(variable[:4], data, unit)

    text_colour = (255, 255, 255)
    back_colour = (0, 170, 170)

    draw.rectangle((0,0,160,80), back_colour)
    draw.text((0, 0), message, font=font, fill=text_colour)
    draw.text((0, 12), cpu_message, font=font, fill=text_colour)

    # Get the IP Address
    new_ip = get_ip()
    new_message = "IP: %s" % new_ip
    draw.text((0, 24), new_message, font=font, fill=text_colour)

    st7735.display(img)


#through testing determined this is needed because flask needs threads dameonised for stuff to run in background
class SensorThread(Thread):
    def __init__(self, socket: SocketIO, interval=5):
        Thread.__init__(self)
        self.socket = socket
        self.interval = interval
        self.lcd_mode = 0

    def run(self):
        self.db_conn = sqlite3.connect(DB_NAME)
        while True:
            if(self.lcd_mode == 2):
                continue
            elif(self.lcd_mode == 0):

                lux = ltr559.get_lux()
                temperature = bme280.get_temperature()
                pressure = bme280.get_pressure()
                humidity = bme280.get_humidity()
                gas_readings = gas.read_all() #gas_readings.reducing, gas_readings.nh3, gas_readings.oxidising
                low, mid, high, amp = noise.get_noise_profile() # What to do with these
                dummy_noise = 100 # for SQL testing purposes
                logging.info("""Light: {:05.02f} Lux
                Temperature: {:05.2f} *C
                Pressure: {:05.2f} hPa
                Relative humidity: {:05.2f} %
                """.format(lux, temperature, pressure, humidity))
                
                display_text("Temperature", temperature, "C")
                timestamp = time.time()*1e3
                self.sql_create(timestamp, temperature, pressure, humidity, lux, 
                dummy_noise, gas_readings.reducing, gas_readings.nh3, gas_readings.oxidising)
                payload = {"timestamp": timestamp, 
                "temperature": temperature,
                "pressure": pressure,
                "humidity": humidity,
                "lux": lux,
                "noise": dummy_noise,
                "reducing": gas_readings.reducing,
                "nh3": gas_readings.nh3,
                "gas_oxidising": gas_readings.nh3}      
                self.socket.emit("sensor", payload)
            time.sleep(self.interval)

    def sql_create(self, timestamp, temp, pressure, humidity, lux, noise, red, nh3, oxi):        
        # sql_query = "INSERT INTO Sensor_Data VALUES ('" + str(temp) + "', ' " + str(pressure) + "' , ' " + str(humidity) + "' , ' " + str(lux) + "' , ' " + str(noise) + "' , ' " + str(red) + "' , ' " + str(nh3) + "' , ' " + str(oxi) + "')"
        sql = """INSERT INTO Sensor_Data(
            timestamp,
            temperature,
            pressure,
            humidity,
            light,
            noise,
            gas_reducing,
            gas_nh3,
            gas_oxidising
        ) 
        VALUES(?,?,?,?,?,?,?,?,?)"""
        sql_vals = (timestamp, temp, pressure, humidity, lux, noise, red, nh3, oxi)
        self.db_conn.execute(sql, sql_vals)   
