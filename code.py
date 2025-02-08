import time
import board
import displayio
import framebufferio
import rgbmatrix
from adafruit_display_text import label
import terminalio  
import requests
from datetime import datetime, timedelta
import json

matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=4,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1
)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

font = terminalio.FONT

date_line = label.Label(font, text="", color=0xFFFFFF)
date_line.x = 3
date_line.y = 5 

time_line = label.Label(font, text="", color=0xFFFFFF)
time_line.x = 8
time_line.y = 13 

weather_line = label.Label(font, text="", color=0xFFFFFF)
weather_line.x = 0
weather_line.y = 21 

bitmap = displayio.OnDiskBitmap("kuromi.bmp")
kuromi_img = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
kuromi_img.x = 35  
kuromi_img.y = -5   

g = displayio.Group()
g.append(kuromi_img)
g.append(date_line)
g.append(time_line)
g.append(weather_line)
display.root_group = g

def fetch_weather():
    API_KEY = "98322b5ee0ff96246ae95f03c9494d6c"
    url = f"http://api.openweathermap.org/data/2.5/weather?q=New+Delhi&appid=98322b5ee0ff96246ae95f03c9494d6c&units=metric"
    
    try:
        response = requests.get(url)
        print("API Response Code:", response.status_code)  

        if response.status_code == 200:
            data = response.json()
            print("Weather Data:", data)  

            temperature = round(data["main"]["temp"]) 
            condition = data["weather"][0]["description"] 
            return temperature, condition
        else:
            print("Error: Invalid API Response", response.text)

    except Exception as e:
        print("Error fetching weather:", e)

    return None, None

last_update = 0

while True:
    now = datetime.now() + timedelta(hours=5, minutes=30)
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%b %d")

    date_line.text = current_date
    time_line.text = current_time

    if time.time() - last_update > 300:
        temperature, condition = fetch_weather()
        if temperature and condition:
            weather_line.text = f"{temperature}C {condition}"
        else:
            weather_line.text = "Weather Unavailable"
        last_update = time.time()

    display.refresh(minimum_frames_per_second=0)

    time.sleep(1)
