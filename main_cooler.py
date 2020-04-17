import gc
import dht
import time
from machine import Pin
from pk import PlantKeeper
import node_type

# Booting
sensor = dht.DHT11(Pin(14))
led = Pin(27, Pin.OUT)
led.on()
time.sleep(1)
led.off()
pk = PlantKeeper(host='10.3.141.1', port=8001)
pk.set_node_type(node_type=node_type.COOLER)

# Main loop
last_power_status = False
init = True
if __name__ == '__main__':
    while True:
        try:
            sensor.measure()
            pk.post(
                {
                    "air_in_temperature": sensor.temperature(),
                    "air_out_temperature": 0,
                    "air_in_humidity": sensor.humidity(),
                    "air_out_humidity": 0,
                    "heater_temperature": 0
                }
            )
            print(pk.json)
            if init:
                last_power_status = pk.power

            if pk.power != last_power_status:
                last_power_status = pk.power
                if pk.power == 0:
                    led.off()
                elif pk.power == 1:
                    led.on()

            init = False
        except OSError:
            pass
        else:
            print('[WAR] Can read sensor on PIN 14')
        gc.collect()
