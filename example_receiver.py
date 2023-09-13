import numpy as np
import cv2
import zmq
from tqdm import tqdm

cap = cv2.VideoCapture(
    "udpsrc address=192.168.123.13 port=9201 "
    "! application/x-rtp,media=video,encoding-name=H264 "
    "! rtph264depay ! h264parse ! omxh264dec ! videoconvert ! appsink"
)

ctx = zmq.Context()
sock = ctx.socket(zmq.DEALER)
sock.set(zmq.CONFLATE, 1)
sock.set(zmq.CONNECT_TIMEOUT, 200)
sock.connect('tcp://192.168.123.1:5555')

with tqdm() as bar:
    while True:
        rv, image = cap.read()
        if not rv:
            continue
        rv, arr = cv2.imencode('.png', image)
        assert rv
        sock.send_pyobj(arr)
        bar.update()
