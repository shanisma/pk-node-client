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
_REGISTRY_SIGN_TOPIC = NODE_TYPE + "/" + NODE_TAG + "/" + "registry"
_REGISTRY_VALIDATION_TOPIC = NODE_TYPE + "/" + NODE_TAG + "/" + "registry/validate"


def read_sensors():
    return ujson.dumps(
        {
            "soil_moisture": random.randint(0, 100)
        }
    )


def controller_callback(topic, msg):
    """
    Handle new message coming from the controller
    :param topic:
    :param msg:
    :return:
    """
    print((topic, msg))


def subscribe_controller():
    while True:
        sub_client.wait_msg()


def publish_sensors():
    while True:
        pub_client.publish(_SENSOR_TOPIC, read_sensors())


registry_client = MQTTClient(NODE_TYPE + "_" + NODE_TAG + "_" + "REGISTRY ", SERVER, PORT)
registry_client.set_callback(controller_callback)

sub_client = MQTTClient(NODE_TYPE + "_" + NODE_TAG + "_" + "SUB", SERVER, PORT)
sub_client.set_callback(controller_callback)
sub_client.connect()
sub_client.subscribe(_CONTROLLER_TOPIC)

pub_client = MQTTClient(NODE_TYPE + "_" + NODE_TAG + "_" + "PUB", SERVER, PORT)
pub_client.connect()

_thread.start_new_thread(publish_sensors, ())
_thread.start_new_thread(subscribe_controller, ())
