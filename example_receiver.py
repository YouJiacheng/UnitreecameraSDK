import numpy as np
import cv2

cap = cv2.VideoCapture(
    "udpsrc address=192.168.123.13 port=9201 "
    "! application/x-rtp,media=video,encoding-name=H264 "
    "! rtph264depay ! h264parse ! omxh264dec ! videoconvert ! appsink"
)


while True:
    rv, image = cap.read()
    print(image.shape)