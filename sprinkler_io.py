from machine import Pin, ADC
from utils import fit

# ======================== Input  =========================
# =========================================================
soi_moisture_sensor = ADC(Pin(34))
soi_moisture_sensor.atten(ADC.ATTN_11DB)
# Use soil_moisture_map to transform
# ADC to percent of water level
soil_moisture_map = fit(
    # Map analog read min/max
    [2330, 1390],
    # to 0% to 100%
    [0, 100]
)


def read_sensors(tag):
    soil_moisture_raw_adc = soi_moisture_sensor.read()
    return {
        "tag": tag,
        "soil_moisture_raw_adc": soil_moisture_raw_adc,
        "soil_moisture": int(soil_moisture_map(soil_moisture_raw_adc))
    }


# ======================== Output  ========================
# =========================================================
water_valve_relay = Pin(26, Pin.OUT)
