'\nConnect to wifi + print to tft screen booting message\nAuthor: Shanmugathas Vigneswaran\nemail: shanmugathas.vigneswaran@outlook.fr\n'
import network
from settings import WIFI_SSID,WIFI_PASSWORD,tft
from utils import boot_display
def connect_access_point():
	A=network.WLAN(network.STA_IF)
	if not A.isconnected():
		print('connecting to network...');A.active(True);A.connect(WIFI_SSID,WIFI_PASSWORD)
		while not A.isconnected():boot_display(tft)
	print('network config:',A.ifconfig())
if __name__=='__main__':connect_access_point()