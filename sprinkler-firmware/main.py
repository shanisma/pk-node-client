_F='Tag: '
_E='last_power'
_D=True
_C='tag'
_B='_'
_A=False
import ujson,random,_thread
from ST7735 import TFT
from sysfont import sysfont
from umqtt.robust import MQTTClient
from settings import tft,MQTT_SERVER,MQTT_PORT,WIFI_SSID
NODE_TYPE='sprinkler'
NODE_TAG='orchid'
_SENSOR_TOPIC=NODE_TYPE+'/sensor'
_CONTROLLER_TOPIC=NODE_TYPE+'/controller'
_REGISTRY_SIGN_TOPIC='sprinkler/config/registry'
_REGISTRY_VALIDATION_TOPIC='sprinkler/config/registry/validation/'+NODE_TAG
registered=_A
flow_dict={_E:_A}
def register():A=MQTTClient(NODE_TYPE+_B+NODE_TAG+'_REG',MQTT_SERVER,MQTT_PORT);A.connect();A.publish(_REGISTRY_SIGN_TOPIC,ujson.dumps({_C:NODE_TAG}))
def wait_registry_response():
	global registered
	def B(topic,msg):global registered;registered=ujson.loads(msg)['acknowledge'];raise ValueError('force close subscription')
	A=MQTTClient(NODE_TYPE+_B+NODE_TAG+'_REG_VALIDATE',MQTT_SERVER,MQTT_PORT);A.set_callback(B);A.connect();A.subscribe(_REGISTRY_VALIDATION_TOPIC)
	try:
		while _D:A.wait_msg()
	finally:A.disconnect()
def subscribe_controller():
	def B(topic,msg):
		A=ujson.loads(msg)
		if A[_C]==NODE_TAG:print((topic,msg))
	A=MQTTClient(NODE_TYPE+_B+NODE_TAG+'_SUB',MQTT_SERVER,MQTT_PORT);A.set_callback(B);A.connect();A.subscribe(_CONTROLLER_TOPIC)
	while _D:A.wait_msg()
def publish_sensors():
	def B():return ujson.dumps({_C:NODE_TAG,'soil_moisture':random.randint(0,100)})
	A=MQTTClient(NODE_TYPE+_B+NODE_TAG+'_PUB',MQTT_SERVER,MQTT_PORT);A.connect()
	while _D:A.publish(_SENSOR_TOPIC,B())
def init_display(_tft):
	A=_tft;global registered;B=WIFI_SSID
	if len(B)>=14:B=WIFI_SSID[0:14]
	A.fill(TFT.BLACK);A.fillrect((0,0),(128,50),TFT.WHITE);A.fillrect((0,50),(128,160),TFT.RED);A.text((2,2),'Wifi:'+B,TFT.BLACK,sysfont,1.1,nowrap=_A);A.text((2,10),'Node:'+NODE_TYPE,TFT.BLACK,sysfont,1.1,nowrap=_A);A.text((2,20),_F+NODE_TAG,TFT.BLACK,sysfont,1.1,nowrap=_A)
	if not registered:A.text((2,30),'WARNING:tag already registered !!!',TFT.BLACK,sysfont,1.1,nowrap=_A)
def update_display(_tft):
	A=_tft;global flow_dict
	if flow_dict[_E]:B=TFT.GREEN
	else:B=TFT.RED
	A.fillrect((0,50),(128,160),B);A.text((2,50),_F+NODE_TAG,TFT.BLACK,sysfont,1.1,nowrap=_A);A.text((2,60),'Raw ADC: ',TFT.BLACK,sysfont,1.1,nowrap=_A);A.text((2,70),'Soil humidity: ',TFT.BLACK,sysfont,1.1,nowrap=_A);A.text((2,80),'Power: ',TFT.BLACK,sysfont,1.1,nowrap=_A)
register()
try:wait_registry_response()
except ValueError:pass
init_display(tft)
_thread.start_new_thread(subscribe_controller,())
_thread.start_new_thread(publish_sensors,())