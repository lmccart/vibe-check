#!/usr/bin/env python
from __future__ import print_function
import datetime
import sys
import json

def log(*args):
    print(str(datetime.datetime.now()), *args)
    sys.stdout.flush()

from RawProcessor import RawProcessor
import cv2
import numpy as np
import arducam_mipicamera as arducam
import v4l2
import os
import errno
import time

def mkdirp(dir_name):
    try:
        os.makedirs(dir_name)
    except OSError as exc: 
        if exc.errno == errno.EEXIST and os.path.isdir(dir_name):
            pass

log('loading config')

# empty default configuration
config = { }

# custom configuration overrides defaults
with open('config.json') as f:
    config.update(json.load(f))

# always start with high exposure
config['exposure'] = 1600

width, height = 4656, 3496
processor = RawProcessor(width, height, mode='bgr')

log('connecting to camera')
camera = arducam.mipi_camera()
camera.init_camera()

log('setting resolution')
camera.set_resolution(width, height)
log('setting exposure and white balance')
camera.software_auto_exposure(enable=False)
camera.software_auto_white_balance(enable=False)
camera.set_control(v4l2.V4L2_CID_EXPOSURE, config['exposure'])
camera.set_control(v4l2.V4L2_CID_FOCUS_ABSOLUTE, config['focus'])

while True:
    log('capturing')
    frame = camera.capture(encoding='raw')

    log('processing image')
    img = processor(frame.as_array)

    clipping = np.sum(img == 1023)
    pixels = width * height * 3
    ratio = float(clipping) / pixels
    log('percent clipping:', 100*ratio)

    if ratio < 0.0001:
        break

    config['exposure'] = int(0.9 * config['exposure'])
    camera.set_control(v4l2.V4L2_CID_EXPOSURE, config['exposure'])
    log('clipping, decreasing exposure to', config['exposure'])

mkdirp('../reference')
for i, bracket in enumerate((0.50, 1.00, 1.50)):
    exposure = int(bracket * config['exposure'])
    camera.set_control(v4l2.V4L2_CID_EXPOSURE, exposure)
    time.sleep(1)
    log('bracketed exposure ', i, '=', exposure)
    frame = camera.capture(encoding='raw')
    frame.as_array.tofile('../reference/' + str(exposure) + '.raw')

log('exiting')
camera.close_camera()