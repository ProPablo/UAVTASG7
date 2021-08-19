import subprocess
from PIL import Image, ImageDraw, ImageFont
# from Roboto-Thin.ttf import RobotoMedium as UserFont
import logging
import os

wifi_interface = "wifi0"

# result = subprocess.run(['ifconfig', 'wifi0', '|', 'grep', '"inet"'], capture_output=True, text=True)
# result = subprocess.run(['ifconfig', 'wifi0'], capture_output=True, text=True)
# result = subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout
result = "172.28.128.1 192.168.56.1 172.19.2.234"
ips = result.split(' ')

logging.basicConfig(\
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""lcd.py - Hello, World! example on the 0.96" LCD.
Press Ctrl+C to exit!
""")

logging.info("Found IP: " + ips[0])

WIDTH = 160
HEIGHT = 80

# New canvas to draw on.
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

# Text settings.
font_size = 25
font_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 'Roboto-Thin.ttf'
    )
)

font = ImageFont.truetype(font_path, font_size)
text_colour = (255, 255, 255)
back_colour = (0, 170, 170)

message = "IP: %s" % ips[2]
size_x, size_y = draw.textsize(message, font)

# Calculate text position
x = (WIDTH - size_x) / 2
y = (HEIGHT / 2) - (size_y / 2)

# Draw background rectangle and write text.
draw.rectangle((0, 0, 160, 80), back_colour)
draw.text((x, y), message, font=font, fill=text_colour)

img.show()