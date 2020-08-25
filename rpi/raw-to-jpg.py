import sys
import os
import numpy as np
import cv2
from camera.RawProcessor import RawProcessor

for fn in sys.argv[1:]:
    out_fn = os.path.splitext(fn)[0] + '.jpg'
    if os.path.exists(out_fn):
        print('skipping', out_fn)
        continue

    data = np.fromfile(fn, dtype=np.uint8)

    width, height = 4656, 3496
    curves = [
        [[0, 16], [127, 110], [255, 255]],
        [[0, 17], [127, 159], [255, 255]],
        [[0, 17], [127, 137], [255, 255]]]
    processor = RawProcessor(width, height, curves, mode='bgr')
    img = processor(data)

    print('saving', out_fn)
    cv2.imwrite(out_fn, img)