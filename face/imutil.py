import cv2
import numpy as np

def imdecode(data):
    if isinstance(data, bytes):
        data = np.fromstring(data, np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    return img[...,::-1]

def imread(filename):
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    return img[...,::-1]

def imwrite(filename, img):
    if img is not None:
        if len(img.shape) > 2:
            img = img[...,::-1]
    return cv2.imwrite(filename, img)