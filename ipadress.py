#!/usr/bin/python
import socket

import ST7735
import os
from time import sleep
from PIL import Image, ImageDraw, ImageFont
import logging


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

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""lcd.py - Hello, World! example on the 0.96" LCD.
Press Ctrl+C to exit!
""")

# Create LCD class instance.
disp = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display.
disp.begin()

# Width and height to calculate text position.
WIDTH = disp.width
HEIGHT = disp.height

# Text settings.
font_size = 17
font_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 'Roboto-Thin.ttf'
    )
)

font = ImageFont.truetype(font_path, font_size)
text_colour = (255, 255, 255)
back_colour = (0, 170, 170)

ip = get_ip()
message = "IP: %s" % ip
logging.info("Found IP: " +ip)
logging.info("display size: " + str(WIDTH) + ", " + str(HEIGHT))

# # New canvas to draw on.
# img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
# draw = ImageDraw.Draw(img)

# size_x, size_y = draw.textsize(message, font)

# # Calculate text position
# x = (WIDTH - size_x) / 2
# y = (HEIGHT / 2) - (size_y / 2)

# # Draw background rectangle and write text.
# draw.rectangle((0, 0, 160, 80), back_colour)
# draw.text((x, y), message, font=font, fill=text_colour)
# disp.display(img)

def display_message(message):
    # New canvas to draw on.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    size_x, size_y = draw.textsize(message, font)

    # Calculate text position
    x = (WIDTH - size_x) / 2
    y = (HEIGHT / 2) - (size_y / 2)

    # Draw background rectangle and write text.
    draw.rectangle((0, 0, 160, 80), back_colour)
    draw.text((x, y), message, font=font, fill=text_colour)
    disp.display(img)

# Keep running.
try:
    while True:
        sleep(5)
        new_ip = get_ip()
        logging.info("New Ip: " +new_ip)
        if (new_ip !=ip):
            new_message = "IP: %s" % new_ip
            display_message(new_message)
            # print("stuff")
        pass

# Turn off backlight on control-c
except KeyboardInterrupt:
    disp.set_backlight(0)