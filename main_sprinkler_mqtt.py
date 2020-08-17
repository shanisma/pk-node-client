import gc
import ujson
import random
import _thread
from ST7735 import TFT
from sysfont import sysfont
from umqtt.robust import MQTTClient
from settings import (
    tft,
    MQTT_SERVER,
    MQTT_PORT,
    WIFI_SSID
)
from utils import register_sprinkler

gc.enable()

NODE_TYPE = "sprinkler"
NODE_TAG = 'orchid'

_SENSOR_TOPIC = NODE_TYPE + "/sensor"
_CONTROLLER_TOPIC = NODE_TYPE + "/controller"
_TFT = tft

registered = False
flow_dict = {
    "current": {
        "water_valve_signal": False,

    },
    "last": {
        "water_valve_signal": False,
    },
    "sensors": {}
}


def subscribe_controller():
    global flow_dict

    def callback(topic, msg):
        d = ujson.loads(msg)
        if d['tag'] == NODE_TAG:
            flow_dict['current']['water_valve_signal'] = d['water_valve_signal']

    c = MQTTClient(
        NODE_TYPE
        + "_"
        + NODE_TAG
        + "_SUB",
        MQTT_SERVER,
        MQTT_PORT
    )
    c.set_callback(callback)
    c.connect()
    c.subscribe(_CONTROLLER_TOPIC)
    while True:
        c.wait_msg()


def publish_sensors():
    global flow_dict

    def read_sensors():
        return {
            "tag": NODE_TAG,
            "soil_moisture": random.randint(0, 100)
        }

    c = MQTTClient(
        NODE_TYPE
        + "_"
        + NODE_TAG
        + "_PUB",
        MQTT_SERVER,
        MQTT_PORT
    )
    c.connect()
    while True:
        s = read_sensors()
        flow_dict['sensors'] = s
        c.publish(_SENSOR_TOPIC, ujson.dumps(s))


def init_display():
    global _TFT, registered
    wifi_ssid = WIFI_SSID
    if len(wifi_ssid) >= 14:
        wifi_ssid = WIFI_SSID[0:14]
    _TFT.fill(TFT.BLACK)
    _TFT.fillrect((0, 0), (128, 50), TFT.WHITE)
    _TFT.text((2, 2), "Wifi:" + wifi_ssid, TFT.BLACK, sysfont, 1.1, nowrap=False)
    _TFT.text((2, 10), "Node:" + NODE_TYPE, TFT.BLACK, sysfont, 1.1, nowrap=False)
    _TFT.text((2, 20), "Tag: " + NODE_TAG, TFT.BLACK, sysfont, 1.1, nowrap=False)
    if not registered:
        _TFT.text((2, 30), "WARNING:tag already registered !!!", TFT.BLACK, sysfont, 1.1, nowrap=False)
        _TFT.fillrect((0, 50), (128, 160), TFT.RED)


def update_display():
    global _TFT, flow_dict
    while True:
        # Flush dynamic part of screen
        _TFT.fillrect((0, 50), (128, 160), TFT.GRAY)
        if flow_dict['current']['water_valve_signal']:
            _TFT.fillrect((110, 50), (20, 10), TFT.GREEN)
            _TFT.text((2, 50), "Water valve on", TFT.BLACK, sysfont, 1.1, nowrap=False)
        else:
            _TFT.fillrect((110, 50), (20, 10), TFT.RED)
            _TFT.text((2, 50), "Water valve off", TFT.BLACK, sysfont, 1.1, nowrap=False)

        _TFT.text((2, 60), "Raw ADC: " + str(flow_dict['sensors']['soil_moisture']), TFT.BLACK, sysfont, 1.1, nowrap=False)
        _TFT.text((2, 70), "Soil moisture: ", TFT.BLACK, sysfont, 1.1, nowrap=False)
        gc.collect()


# =================================
# Register tag to Master
# =================================
registered = register_sprinkler(NODE_TAG)
init_display()
# =================================
# Subscription to controller
# =================================
_thread.start_new_thread(subscribe_controller, ())

# =================================
# Subscription to controller
# =================================
_thread.start_new_thread(publish_sensors, ())

# =================================
# Update TFT screen
# =================================
_thread.start_new_thread(update_display, ())
