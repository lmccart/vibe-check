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
import time
from requests.exceptions import ConnectionError

print('loading configuration')

# mostly disable during specific times
slow_begin_utc_hour = 21 # begin at 9pm UTC, 11pm denmark time
slow_end_utc_hour = 3 # end at 3am UTC, 5am denmark time
slow_sleep_duration = 60 # only one frame per minute when disabled
prev_slow_status = None

# default configuration
min_exposure = 1280
max_exposure = 128000
config = {
    'id': 0,
    'exposure': 12800,
    'focus': 100,
    'curves': [
        # [[0, 16], [127, 110], [255, 255]], # daylight
        # [[0, 17], [127, 159], [255, 255]],
        # [[0, 17], [127, 107], [255, 255]]]

        # [[0,0], [127,103], [255,255]], # basic white balance
        # [[0,0], [127,130], [255,255]],
        # [[0,0], [127,58], [255,255]]]

        [[0, 17], [127,103], [255, 197]], # exhibition
        [[0, 17], [127,130], [255, 233]],
        [[0, 17], [127,58], [255, 99]]]
}

# custom configuration overrides defaults
with open('config.json') as f:
    config.update(json.load(f))

host = 'vibecheck.local'
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

def pct_overexposed(img, pts=16):
    h,w = img.shape[:2]
    overexposed = 0
    for y in np.linspace(0, h, pts, endpoint=False, dtype=int):
        for x in np.linspace(0, w, pts, endpoint=False, dtype=int):
            if np.any(img[y,x] == 255):
                overexposed += 1
    return float(overexposed) / (pts ** 2)

def modify_exposure(multiplier):
    config['exposure'] *= multiplier
    config['exposure'] = np.clip(config['exposure'], min_exposure, max_exposure)
    config['exposure'] = int(config['exposure'])
    # if multiplier > 1:
    #     print('increasing exposure to', config['exposure'])
    # else:
    #     print('decreasing exposure to', config['exposure'])
    camera.set_control(v4l2.V4L2_CID_EXPOSURE, config['exposure'])

def capture_and_send():
    global prev_slow_status
    
    # uncomment to update in realtime

    # with open('config.json') as f:
    #     config.update(json.load(f))
    # camera.set_control(v4l2.V4L2_CID_EXPOSURE, config['exposure'])
    # camera.set_control(v4l2.V4L2_CID_FOCUS_ABSOLUTE, config['focus'])

    # capture image
    frame = camera.capture(encoding='raw')

    # process image
    img = processor(frame.as_array)

    # get exposure advice and autoexpose
    overexposed = pct_overexposed(img)
    # print('overexposed', overexposed)
    if overexposed > 0.02:
        modify_exposure(0.99)
    if overexposed == 0:
        modify_exposure(1.01)

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

    # run slowly during off-hours
    hour = datetime.datetime.utcnow().hour
    slow_status = hour > slow_begin_utc_hour or hour < slow_end_utc_hour
    if slow_status != prev_slow_status:
        log('slow mode' if slow_status else 'full speed mode')
    if slow_status:
        time.sleep(slow_sleep_duration)
    prev_slow_status = slow_status

log('capturing')
while True:
    try:
        capture_and_send()
    except KeyboardInterrupt:
        break

log('exiting')
camera.close_camera()