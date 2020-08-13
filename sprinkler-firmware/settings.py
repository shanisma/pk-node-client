from machine import SPI,Pin,ADC
from utils import fit
from ST7735 import TFT
WIFI_SSID=''
WIFI_PASSWORD=''
MQTT_SERVER=''
MQTT_PORT=32500
SPI=SPI(2,baudrate=20000000,polarity=0,phase=0,sck=Pin(18),mosi=Pin(23),miso=Pin(12))
POWER_COLOR=TFT.GREEN
tft=TFT(SPI,2,4,15)
tft.initb2()
tft.rgb(True)
soil_moisture_sensor=ADC(Pin(34))
soil_moisture_sensor.atten(ADC.ATTN_11DB)
soil_moisture_model=fit([2300,1360],[0,100])
sprinkler_valve=Pin(26,Pin.OUT)
