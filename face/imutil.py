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

def safe_crop(arr, tblr, fill=None):
    n,s,w,e = tblr
    shape = np.asarray(arr.shape)
    shape[:2] = s - n, e - w
    no, so, wo, eo = 0, shape[0], 0, shape[1]
    if n < 0:
        no += -n
        n = 0
    if w < 0:
        wo += -w
        w = 0
    if s >= arr.shape[0]:
        so -= s - arr.shape[0]
        s = arr.shape[0]
    if e >= arr.shape[1]:
        eo -= e - arr.shape[1]
        e = arr.shape[1]
    cropped = arr[n:s,w:e]
    if fill is None:
        return cropped
    out = np.empty(shape, dtype=arr.dtype)
    out.fill(fill)
    try:
        out[no:so,wo:eo] = cropped
    except ValueError:
        # this happens when there is no overlap
        pass
    return out