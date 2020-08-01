import _thread
from umqtt.robust import MQTTClient
import random
import ujson

SERVER = "af120153-db6a-4fdd-a81b-6d902b00e936.nodes.k8s.fr-par.scw.cloud"
PORT = 32500
NODE_TYPE = "sprinkler"
NODE_TAG = 'orchid'

_SENSOR_TOPIC = NODE_TYPE + "/" + NODE_TAG + "/" + "sensor"
_CONTROLLER_TOPIC = NODE_TYPE + "/" + NODE_TAG + "/" + "controller"

pub_client = MQTTClient("umqtt_client", SERVER, PORT)
pub_client.connect()

sub_client = MQTTClient("umqtt_client", SERVER, PORT)
sub_client.connect()


def read_sensors():
    return ujson.dumps({"humidity_level": random.randint(0, 100)})


def publish_sensors():
    while True:
        pub_client.publish(_SENSOR_TOPIC, read_sensors())

_thread.start_new_thread(publish_sensors, ())
