import time
from rtc_featherwing.mpy import rtc
import board
import socket
import displayio
import framebufferio
import rgbmatrix
import terminalio
import adafruit_display_text.label
import adafruit_imageload

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=3,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1
)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

def get_ntp_time(timezone):
    host = "worldtimeapi.org"
    path = f"/api/timezone/{timezone}"

    s = socket.socket()
    s.connect((host, 80))
    s.send(bytes(f"GET {path} HTTP/1.0\r\nHost: {host}\r\n\r\n", "utf-8"))

    response = s.recv(1024).decode("utf-8")
    s.close()

    for line in response.split("\n"):
        if '"datetime":"' in line:
            datetime_str = line.split('"datetime":"')[1].split('"')[0]
            year, month, day = map(int, datetime_str[:10].split("-"))
            hour, minute, second = map(int, datetime_str[11:19].split(":"))
            
            return time.struct_time((year, month, day, hour, minute, second, 0, -1, -1))

ny_time = get_ntp_time("America/New_York")
delhi_time = get_ntp_time("Asia/Kolkata")


rtc.RTC().datetime = ny_time

def get_weather(city):
    api_key = "API_KEY"  
    host = "api.openweathermap.org"
    path = f"/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    s = socket.socket()
    s.connect((host, 80))
    s.send(bytes(f"GET {path} HTTP/1.0\r\nHost: {host}\r\n\r\n", "utf-8"))

    response = s.recv(1024).decode("utf-8")
    s.close()

    for line in response.split("\n"):
        if '"temp":' in line:
            temp = line.split('"temp":')[1].split(",")[0]
            return f"{city}: {temp}°C"

ny_weather = get_weather("New York")
delhi_weather = get_weather("New Delhi")

kuromi_bitmap, palette = adafruit_imageload.load("/kuromi.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
kuromi_tilegrid = displayio.TileGrid(kuromi_bitmap, pixel_shader=palette, x=0, y=0)

line1 = adafruit_display_text.label.Label(terminalio.FONT, color=0xFFFFFF, text=f"New York: {ny_time.tm_hour}:{ny_time.tm_min} AM")
line1.x = 22
line1.y = 8

line2 = adafruit_display_text.label.Label(terminalio.FONT, color=0xFFFFFF, text=f"Delhi: {delhi_time.tm_hour}:{delhi_time.tm_min} AM")
line2.x = 22
line2.y = 20

weather1 = adafruit_display_text.label.Label(terminalio.FONT, color=0x00FF00, text=ny_weather)
weather1.x = 2
weather1.y = 28

weather2 = adafruit_display_text.label.Label(terminalio.FONT, color=0x00FF00, text=delhi_weather)
weather2.x = 2
weather2.y = 40

lyrics = adafruit_display_text.label.Label(terminalio.FONT, color=0xFFC0CB, text="🎵 Taylor Swift - Lyrics scrolling...")
lyrics.x = display.width
lyrics.y = 52

g = displayio.Group()
g.append(kuromi_tilegrid)  
g.append(line1)
g.append(line2)
g.append(weather1)
g.append(weather2)
g.append(lyrics)
display.root_group = g

def scroll(line):
    line.x -= 1
    if line.x < -line.bounding_box[2]:
        line.x = display.width

while True:
    scroll(lyrics) 
    display.refresh(minimum_frames_per_second=0)
