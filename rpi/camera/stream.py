#!/usr/bin/env python
from __future__ import print_function
import datetime
import sys

def log(*args):
    print(str(datetime.datetime.now()), *args)
    sys.stdout.flush()

log('loading libraries')

import json
from RawProcessor import RawProcessor
import cv2
import arducam_mipicamera as arducam
import v4l2
import numpy as np
import requests
from requests.exceptions import ConnectionError

# default configuration
config = {
    'id': 0,
    'exposure': 12800,
    'focus': 100,
    'curves': [
        # [[0, 16], [127, 110], [255, 255]], # daylight
        # [[0, 17], [127, 159], [255, 255]],
        # [[0, 17], [127, 107], [255, 255]]]
        [[0, 17], [127,103], [255, 197]], # exhibition
        [[0, 17], [127,130], [255, 233]],
        [[0, 17], [127,58], [255, 99]]]
}

# custom configuration overrides defaults
with open('config.json') as f:
    config.update(json.load(f))

host = 'hek-dual-gpu.local'
# host = 'iyoiyo-gpu.local'
url = 'http://' + host + ':5000/vibecheck/upload/' + str(config['id'])
jpeg_quality = 90
width, height = 4656, 3496

# swap curves to bgr
processor = RawProcessor(width, height, config['curves'][::-1], 'bgr')

log('connecting to camera')
camera = arducam.mipi_camera()
camera.init_camera()

log('configuring camera')
camera.set_resolution(width, height)
camera.software_auto_exposure(enable=False)
camera.software_auto_white_balance(enable=False)
camera.set_control(v4l2.V4L2_CID_EXPOSURE, config['exposure'])
camera.set_control(v4l2.V4L2_CID_FOCUS_ABSOLUTE, config['focus'])

def capture_and_send():
    with open('config.json') as f:
        config.update(json.load(f))
    camera.set_control(v4l2.V4L2_CID_EXPOSURE, config['exposure'])
    camera.set_control(v4l2.V4L2_CID_FOCUS_ABSOLUTE, config['focus'])

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