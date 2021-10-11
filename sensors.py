from threading import Thread
import time
import socket
import os
import logging
from flask_socketio import SocketIO
import ST7735  # LCD
from bme280 import BME280  # Temperature, Humidity, Pressure

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont

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

# Displays data and text on the 0.96" LCD


def display_text(variable, data, unit):
    # Format the variable name and value
    message = "{}: {:.1f} {}".format(variable[:4], data, unit)

    text_colour = (255, 255, 255)
    back_colour = (0, 170, 170)

    draw.rectangle((0, 0, 160, 80), back_colour)
    draw.text((0, 0), message, font=font, fill=text_colour)

    # Get the IP Address
    new_ip = get_ip()
    new_message = "IP: %s" % new_ip
    draw.text((0, 12), new_message, font=font, fill=text_colour)

    st7735.display(img)


# class SensorThreadOLD(Thread):
#     def __init__(self, filename):
#         Thread.__init__(self)

#     def run():
#         while True:
#         lux = ltr559.get_lux()
#         #prox = ltr559.get_proximity()
#         temperature = bme280.get_temperature()
#         pressure = bme280.get_pressure()
#         humidity = bme280.get_humidity()
#         logging.info("""Light: {:05.02f} Lux
# Temperature: {:05.2f} *C
# Pressure: {:05.2f} hPa
# Relative humidity: {:05.2f} %

# """.format(lux, temperature, pressure, humidity))

#         display_text("Temperature", temperature, "C")
#         time.sleep(1.0)


class SensorThread(Thread):
    def __init__(self, socket: SocketIO, interval=5):
        Thread.__init__(self)
        self.socket = socket
        self.interval = interval

    def run(self):
        while True:
            
            
            self.socket.emit("sensor", {"data": "summing", "counter": self.counter})
            time.sleep(self.interval)
