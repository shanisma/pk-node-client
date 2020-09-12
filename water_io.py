"""
Node Type Water I/O function and configuration
Author: Shanmugathas Vigneswaran
Email: shanmugathas.vigneswaran@outlooK.fr
"""

from machine import Pin, ADC
from utils import fit
from hcsr04 import HCSR04
from influxdb_line_protocol import Metric
from keyestudio import KS0429TdsMeterV1

WATER_TEMPERATURE_IN_CELSIUS = 25

# ======================== Input  =========================
# =========================================================
# -------------- Water level ultrasonic
water_level_sensor = HCSR04(trigger_pin=21, echo_pin=22, echo_timeout_us=10000)
water_level_fitter = fit(
    # Map analog read min/max
    [118, 34],
    # to 0% to 100%
    [0, 100]
)
# -------------- ph Sensor
# https://en.wikipedia.org/wiki/PH
ph_sensor = ADC(Pin(33))
# set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
ph_sensor.atten(ADC.ATTN_11DB)
ph_fitter = fit(
    # Map analog read min/max
    # don't change this values for ADC
    [0, 4095],
    # acidity level
    [0, 14]
)
# -------------- EC Sensors (nutrient level in water)
# https://en.wikipedia.org/wiki/Conductivity_(electrolytic)
# Default sensor  KeyStudio TDS Meter : https://wiki.keyestudio.com/KS0429_keyestudio_TDS_Meter_V1.0
ec_sensor = ADC(Pin(34))
# set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
ec_sensor.atten(ADC.ATTN_11DB)

# https://en.wikipedia.org/wiki/Reduction_potential
orp_sensor = ADC(Pin(35))
# set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
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


def _limit(x, _min, _max):
    if x < _min:
        return _min
    elif x > _max:
        return _max


def read_sensors():
    water_distance_mm = int(water_level_sensor.distance_mm())
    water_level = int(water_level_fitter(water_distance_mm))
    # limit between 0 and 100
    water_level = _limit(water_level, 0, 100)
    ph_raw_adc = ph_sensor.read()
    ph = int(ph_fitter(ph_raw_adc))

    ec_raw_adc = ec_sensor.read()
    ec = KS0429TdsMeterV1().raw_adc_to_ppm(ec_raw_adc, WATER_TEMPERATURE_IN_CELSIUS)

    orp_raw_adc = orp_sensor.read()
    orp = int(orp_fitter(orp_raw_adc))

    metric = Metric("water")
    metric.add_value('water_distance_mm', water_distance_mm)
    metric.add_value('water_level', water_level)
    metric.add_value('ph_raw_adc', ph_raw_adc)
    metric.add_value('ph', ph)
    metric.add_value('ec_raw_adc', ec_raw_adc)
    metric.add_value('ec', ec)
    metric.add_value('orp_raw_adc', orp_raw_adc)
    metric.add_value('orp', orp)

    return {
        "water_distance_mm": water_distance_mm,
        "water_level": water_level,
        "ph_raw_adc": ph_raw_adc,
        "ph": ph,
        "ec_raw_adc": ec_raw_adc,
        "ec": ec,
        "orp_raw_adc": orp_raw_adc,
        "orp": orp,
        "influx_message": str(metric)
    }


# ======================== Output  ========================
# =========================================================
water_pump_relay = Pin(19, Pin.OUT)
nutrient_pump_relay = Pin(16, Pin.OUT)
ph_downer_pump_relay = Pin(5, Pin.OUT)
