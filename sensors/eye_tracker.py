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
GAZE_DIRECTION_KEY = "gd"
EYE_KEY = "eye"


def stream_gaze_data(callback, timeout=1, smooth_zeros=True):
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
    left_direction = [0, 0, 0]
    right_direction = [0, 0, 0]

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
        if GAZE_DIRECTION_KEY in live_data:
            if live_data[EYE_KEY] == "right":
                right_direction = live_data[GAZE_DIRECTION_KEY]
            else:
                left_direction = live_data[GAZE_DIRECTION_KEY]
        if GAZE_DIRECTION_KEY in live_data or PUPIL_DIAMETER_KEY in live_data:
            callback(left_diameter, right_diameter, left_direction, right_direction)


def stream_to_lsl():
    pd_info = StreamInfo("Eye tracking - pupil diameter", "Gaze", 2)
    pd_outlet = StreamOutlet(pd_info)
    gd_info = StreamInfo("Eye tracking - Gaze direction", "Gaze", 6)
    gd_outlet = StreamOutlet(gd_info)

    def callback(left_pd, right_pd, left_gd, right_gd):
        pd_outlet.push_sample([left_pd, right_pd])
        gd_outlet.push_sample(left_gd + right_gd)
    stream_gaze_data(callback)


if __name__ == '__main__':
    stream_to_lsl()
