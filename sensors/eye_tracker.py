import select
import socket
import json
import time
import uuid
from pylsl import StreamInfo, StreamOutlet


TRACKER_ADDR = ("192.168.71.50", 49152)
RECV_BUFFER_SIZE = 1024
KEEPALIVE_DATA = json.dumps({"op": "start", "type": "live.data.unicast", "key": str(uuid.uuid4())}).encode("ascii")
KEEPALIVE_FREQ = 2
PUPIL_DIAMETER_KEY = "pd"
EYE_KEY = "eye"


def stream_pupil_diameter(callback, timeout=1, smooth_zeros=True):
    """
    Stream pupil diamater info from Tobii eye tracker to a callback function

    :param callback: a function that receives 2 arguments (left_diameter, right_diameter)
    :param timeout: maximum timeout to receive data
    :param smooth_zeros: whether to ignore zero diameter (caused by blinking usually)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.sendto(KEEPALIVE_DATA, TRACKER_ADDR)
    last_ka_time = time.time()

    left_diameter = 0
    right_diameter = 0

    while select.select([sock], [], [], timeout)[0]:
        if time.time() - last_ka_time > KEEPALIVE_FREQ:
            sock.sendto(KEEPALIVE_DATA, TRACKER_ADDR)
            last_ka_time = time.time()

        live_data = json.loads(sock.recv(RECV_BUFFER_SIZE))
        if PUPIL_DIAMETER_KEY in live_data:
            if live_data[PUPIL_DIAMETER_KEY] != 0 or not smooth_zeros:
                if live_data[EYE_KEY] == "right":
                    right_diameter = live_data[PUPIL_DIAMETER_KEY]
                else:
                    left_diameter = live_data[PUPIL_DIAMETER_KEY]
            callback(left_diameter, right_diameter)


def stream_to_lsl():
    info = StreamInfo("Eye tracking", "Gaze", 2)
    outlet = StreamOutlet(info)

    stream_pupil_diameter(lambda left_d, right_d: outlet.push_sample([left_d, right_d]))


if __name__ == '__main__':
    stream_to_lsl()
