"""

Plant keeper Water ESP32 firmware
Use:
    - Pin 21 for HCSR04 trigger, 22 for echo, use +5V not +3.3V
    - Pin 26 for Pump activation
    - TFT Screen ST7735 Pins: 4, 2, 23, 18, 15
        tested with supplier = Az Delevery

Author : Shanmugathas Vigneswaran
mail : shangmuathas.vigneswaran@outlook.fr

"""
__version__ = 'wip-no-release'

import gc
import time
from boot import SSID
from sysfont import sysfont
from ST7735 import TFT
from hcsr04 import HCSR04
from machine import SPI, Pin, ADC
from utils import fit
from pk import PlantKeeper
import node_type

# Node and Api Gateway setting
NODE_TYPE = node_type.WATER
PK_API_GATEWAY_HOST = '192.168.0.5'
PK_API_GATEWAY_PORT = 31801
# Soil humidity sensors setting
water_level_sensor = HCSR04(trigger_pin=21, echo_pin=22, echo_timeout_us=10000)
water_level_fitter = fit(
    # Map analog read min/max
    [118, 34],
    # to 0% to 100%
    [0, 100]
)

# https://en.wikipedia.org/wiki/PH
ph_sensor = ADC(Pin(33))
ph_sensor.atten(ADC.ATTN_11DB)
ph_fitter = fit(
    # Map analog read min/max
    # don't change this values for ADC
    [0, 4095],
    # acidity level
    [0, 14]
)

# https://en.wikipedia.org/wiki/Conductivity_(electrolytic)
ec_sensor = ADC(Pin(34))
ec_sensor.atten(ADC.ATTN_11DB)
ec_fitter = fit(
    # Map analog read min/max
    # don't change this values for ADC
    [0, 4095],
    # depends on used sensor
    # target default range [5 ; 50]
    # units mS/m
    [5, 50]
)

# https://en.wikipedia.org/wiki/Reduction_potential
orp_sensor = ADC(Pin(35))
orp_sensor.atten(ADC.ATTN_11DB)
orp_fitter = fit(
    # Map analog read min/max
    # don't change this values for ADC
    [0, 4095],
    # depend on used sensor
    # target default range [-400 ; 400]
    # units milliVolt
    [-400, 400]
)

# Relay for valve power on / power off
PUMP_RELAY = Pin(26, Pin.OUT)

SPI = SPI(
    2, baudrate=20000000,
    polarity=0, phase=0,
    sck=Pin(18), mosi=Pin(23), miso=Pin(12)
)
POWER_COLOR = TFT.GREEN

# Print Node information / Static section
tft = TFT(SPI, 2, 4, 15)
tft.initb2()
tft.rgb(True)
tft.fill(TFT.BLACK)
tft.fillrect((0, 0), (128, 50), TFT.WHITE)
tft.fillrect((0, 50), (128, 160), TFT.RED)
tft.text((2, 2), "Wifi: " + SSID, TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 10), "Api Gateway:", TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 20), PK_API_GATEWAY_HOST + ":" + str(PK_API_GATEWAY_PORT), TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 30), "NodeType:", TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 40), NODE_TYPE, TFT.BLACK, sysfont, 1.1, nowrap=False)

# Create Plant Keeper Client
pk = PlantKeeper(
    host=PK_API_GATEWAY_HOST,
    port=PK_API_GATEWAY_PORT
)
pk.set_node_type(node_type=NODE_TYPE)

while not pk.is_gateway_up():
    tft.fillrect((0, 50), (128, 160), TFT.RED)
    tft.text((2, 60), "ERROR ", TFT.BLACK, sysfont, 2, nowrap=False)
    tft.text((2, 80), "Can not reach Api-Gateway, is Api-Gateway up ?", TFT.BLACK, sysfont, 1.1, nowrap=False)
    gc.collect()
    time.sleep(2)

last_power = False
if __name__ == '__main__':
    while True:
        try:
            raw_distance = water_level_sensor.distance_mm()
            percent = int(water_level_fitter(raw_distance))

            ph_raw = ph_sensor.read()
            ph = ph_fitter(ph_raw)

            ec_raw = ec_sensor.read()
            ec = ec_fitter(ec_raw)

            orp_raw = orp_sensor.read()
            orp = orp_fitter(orp_raw)

            # Post to Api Gateway sensor value
            pk.post({"level": percent})
            # +----------------------------------------------------+
            # | Builtin TFT screen processing (dynamic zone)       |
            # +----------------------------------------------------+
            # full back ground GREEN = Power ON / RED = Power OFF
            if last_power:
                POWER_COLOR = TFT.GREEN
            else:
                POWER_COLOR = TFT.RED
            # Flush dynamic part of screen
            tft.fillrect((0, 50), (128, 160), POWER_COLOR)
            # Print relevant values for user
            tft.text((2, 50), "Raw dist. (mm) : " + str(raw_distance), TFT.BLACK, sysfont, 1.1, nowrap=False)
            tft.text((2, 60), "Water filled %: " + str(percent), TFT.BLACK, sysfont, 1.1, nowrap=False)

            tft.text((2, 70), "pH raw: " + str(ph_raw), TFT.BLACK, sysfont, 1.1, nowrap=False)
            tft.text((2, 80), "pH : " + str(ph), TFT.BLACK, sysfont, 1.1, nowrap=False)

            tft.text((2, 90), "EC raw: " + str(ec_raw), TFT.BLACK, sysfont, 1.1, nowrap=False)
            tft.text((2, 100), "EC (mS/m) :  " + str(ec), TFT.BLACK, sysfont, 1.1, nowrap=False)

            tft.text((2, 110), "ORP raw: " + str(orp_raw), TFT.BLACK, sysfont, 1.1, nowrap=False)
            tft.text((2, 120), "ORP (mV): " + str(orp), TFT.BLACK, sysfont, 1.1, nowrap=False)

            tft.text((2, 130), "Power: " + str(pk.power), TFT.BLACK, sysfont, 1.1, nowrap=False)
            # +----------------------------------------------------+
            # | Activate / Deactivate relay                        |
            # +----------------------------------------------------+
            if not last_power:
                last_power = pk.power
                PUMP_RELAY.value(pk.power)
            else:
                if pk.power != last_power:
                    PUMP_RELAY.value(pk.power)
            last_power = pk.power

            gc.collect()
            time.sleep(0.5)
        except Exception as ex:
            PUMP_RELAY.value(0)
            last_power = 0
            tft.text((2, 60), "ERROR ", TFT.BLACK, sysfont, 2, nowrap=False)
            tft.text(
                (2, 80),
                str(ex.__class__.__name__) + ":" + str(ex),
                TFT.BLACK,
                sysfont,
                1.2,
                nowrap=False
            )
            gc.collect()
            time.sleep(2)
