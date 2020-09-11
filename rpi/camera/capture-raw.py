#!/usr/bin/env python
from __future__ import print_function
import datetime
import sys
import json

def log(*args):
    print(str(datetime.datetime.now()), *args)
    sys.stdout.flush()

from RawProcessor import RawProcessor, zebra, remove_padding_and_unpack_quarter_bgr_preview
import cv2
import numpy as np
import arducam_mipicamera as arducam
import v4l2
import os
import errno
import time
import sys

def mkdirp(dir_name):
    try:
        os.makedirs(dir_name)
    except OSError as exc: 
        if exc.errno == errno.EEXIST and os.path.isdir(dir_name):
            pass

log('loading config')

# empty default configuration
config = {
    'exposure': 1600
}

# custom configuration overrides defaults
with open('config.json') as f:
    config.update(json.load(f))

if len(sys.argv) > 1:
    config['exposure'] = int(sys.argv[1])
    print('overriding exposure with', config['exposure'])

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

# while True:
#     log('capturing')
#     frame = camera.capture(encoding='raw')

#     log('processing image')
#     img = processor(frame.as_array)

#     clipping = np.sum(img == 1023)
#     pixels = width * height * 3
#     ratio = float(clipping) / pixels
#     log('percent clipping:', 100*ratio)

#     if ratio < 0.0001:
#         break

#     config['exposure'] = int(0.9 * config['exposure'])
#     camera.set_control(v4l2.V4L2_CID_EXPOSURE, config['exposure'])
#     log('clipping, decreasing exposure to', config['exposure'])

mkdirp('../reference')
preview = np.zeros((height//4, width//4, 3), np.uint8)
for i, bracket in enumerate((1.0,)): #(0.80, 1.00, 1.20)):
    exposure = int(bracket * config['exposure'])
# for i, exposure in enumerate((25600, 12800, 6400, 3200)):
    camera.set_control(v4l2.V4L2_CID_EXPOSURE, exposure)
    time.sleep(1)
    log('bracketed exposure ', i, '=', exposure)
    frame = camera.capture(encoding='raw')

    remove_padding_and_unpack_quarter_bgr_preview(frame.as_array, width, height, 10, preview.reshape(-1))
    zebra(preview.reshape(-1), width//4, height//4)
    cv2.imwrite('../reference/preview.jpg', preview)

    frame.as_array.tofile('../reference/' + str(exposure) + '.raw')

log('exiting')
camera.close_camera()