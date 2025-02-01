# a quickly "hacked together" hack hour clock for hackatime =)

import random
import time
import requests
import base64

# PLEASE INSERT YOUR HACKATIME API KEY HERE
API_KEY = "

headers = {
    "Authorization": "Basic " + base64.b64encode(API_KEY.encode()).decode()
}

import board
import displayio
import framebufferio
import rgbmatrix

displayio.release_displays()


matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=8,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)
SCALE = 1
b1 = displayio.Bitmap(display.width//SCALE, display.height//SCALE, 2)
b2 = displayio.Bitmap(display.width//SCALE, display.height//SCALE, 2)
palette = displayio.Palette(2)
tg1 = displayio.TileGrid(b1, pixel_shader=palette)
tg2 = displayio.TileGrid(b2, pixel_shader=palette)
g1 = displayio.Group(scale=SCALE)
g1.append(tg1)
display.root_group = g1
g2 = displayio.Group(scale=SCALE)
g2.append(tg2)

display.auto_refresh = True

# mostly borrowed from example
import adafruit_display_text.label
import adafruit_display_text.scrolling_label
import adafruit_display_shapes.rect
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio

line1 = adafruit_display_text.scrolling_label.ScrollingLabel(
    terminalio.FONT,
    color=0xff0000,
    text="pls")
line1.x = 12
line1.y = 8

line2 = adafruit_display_text.scrolling_label.ScrollingLabel(
    terminalio.FONT,
    color=0x0000ff,
    text="wait")
line2.x = 2
line2.y = 24

# Put each line of text into a Group, then show that group.
g = displayio.Group()
background = adafruit_display_shapes.rect.Rect(0,0,64,32)
# backlight a bit?
background.fill = 0x111111
g.append(background)
g.append(line1)
g.append(line2)
display.root_group = g

# You can add more effects in this loop. For instance, maybe you want to set the
# color of each label to a different value.

def wait(secs):
    for i in range(secs * 20):
        line1.update()
        line2.update()
        time.sleep(0.05)

def judge_time(minutes):
    if minutes <= 10:
        line1.color = 0xffffff # white
    elif minutes <= 15:
        line1.color = 0xff0000 # red
    elif minutes <= 30:
        line1.color = 0xffa500 # orange
    elif minutes <= 45:
        line1.color = 0x0000ff # blue
    elif minutes <= 60:
        line1.color = 0xffff00 # yellow
    else:
        line1.color = 0x00ff00 # green

# so i'll def have to rewrite this for the microcontroller
# if wakatime had a SSE api that'd be really cool but we'll have to do slow polling for now
with requests.Session() as sess:
    try:
        resp = sess.get("https://waka.hackclub.com/api/users/current/statusbar/today", headers = headers)
        data = resp.json()["data"]
        item = data["categories"][0]
        line1.text = item["digital"]
        line2.text = item["name"]
        judge_time(item["minutes"])
        wait(30)
        # project
        item = data["projects"][0]
        line1.text = item["digital"]
        line2.text = item["name"]
        judge_time(item["minutes"])
        wait(30)
        # hey, this assumes you work on one project today cause i haven't figured out how to make the api tell the currently active project yet
    except Exception as ex:
        print(ex)
        line1.color = 0xff0000
        line2.color = 0xff0000
        line1.text = "ERROR"
        line2.text = "at " + str(time.time())
        wait(10)
    while True:
        display.refresh(minimum_frames_per_second=0)
