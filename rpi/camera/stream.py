from __future__ import print_function
import datetime

def log(*args):
    print(str(datetime.datetime.now()), *args)

log('loading libraries')

from RawProcessor import RawProcessor
import cv2
import arducam_mipicamera as arducam
import v4l2
import numpy as np
import requests
from requests.exceptions import ConnectionError

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--id', type=int, default=0)
args = parser.parse_args()

host = 'kyle.local'
url = 'http://' + host + ':5000/vibecheck/upload/' + str(args.id)
exposure = 400
focus = 100
jpeg_quality = 90
width, height = 4656, 3496
curves = [
    [[0, 16], [127, 110], [255, 255]],
    [[0, 17], [127, 159], [255, 255]],
    [[0, 17], [127, 137], [255, 255]]]

# swap curves to bgr
processor = RawProcessor(width, height, curves[::-1], 'bgr')

log('connecting to camera')
camera = arducam.mipi_camera()
camera.init_camera()

log('configuring camera')
camera.set_resolution(width, height)
camera.software_auto_exposure(enable=False)
camera.software_auto_white_balance(enable=False)
camera.set_control(v4l2.V4L2_CID_EXPOSURE, exposure)
camera.set_control(v4l2.V4L2_CID_FOCUS_ABSOLUTE, focus)

def capture_and_send():
    # capture image
    frame = camera.capture(encoding='raw')

    # process image
    img = processor(frame.as_array)

    # convert to jpeg
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
    _, encimg = cv2.imencode('.jpg', img, encode_param)

    # upload to server
    data = encimg.tostring()
    headers = {'content-type': 'image/jpeg'}
    try:
        requests.post(url, data=data, headers=headers)
        mb = float(len(data)) / (1000 * 1000)
        log('sent', round(mb, 2), 'MB')
    except ConnectionError:
        log('connection error')

log('capturing')
while True:
    try:
        capture_and_send()
    except KeyboardInterrupt:
        break

log('exiting')
camera.close_camera()