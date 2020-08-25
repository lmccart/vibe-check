import dlib
import onnxruntime as ort
import cv2
import numpy as np

def rgb_to_gray(img):
    return img.mean(axis=-1)[...,np.newaxis].repeat(3,-1)

def preprocess(img):
    x = cv2.resize(img, (96,96))
    x = x.astype(np.float32)
    x -= 127.5
    x /= 127.5
    x = rgb_to_gray(x)
    return x[np.newaxis]

def softmax(x):
    x = np.exp(x)
    return x / x.sum()

def resize_rect(rect, upsample):
    tblr = (rect.top(), rect.bottom(), rect.left(), rect.right())
    return (np.asarray(tblr) * upsample).astype(int).tolist()

def resize_shape(shape, upsample):
    parts = [(e.x, e.y) for e in shape.parts()]
    return (np.asarray(parts) * upsample).astype(int).tolist()
    
def dlib_crop(img, rect):
    t,b,l,r = (rect.top(), rect.bottom(), rect.left(), rect.right())
    return img[t:b,l:r]

class FaceAnalyzer:
    def __init__(self):
        # switch to http://dlib.net/cnn_face_detector.py.html or blazeface
        self.face_detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor('models/shape_predictor_5_face_landmarks.dat')
        self.face_recognizer = dlib.face_recognition_model_v1('models/dlib_face_recognition_resnet_model_v1.dat')
        self.expression_classifier = ort.InferenceSession('models/ferplus-mobilenetv2-0.830.onnx')
        with open('models/ferplus_classes.txt') as f:
            self.expression_classes = f.read().splitlines()

    def __call__(self, img, downsample=2):
        height, width = img.shape[:2]
        img_small = cv2.resize(img, (width//downsample, height//downsample))
        rects = self.face_detector(img_small, 0) # 500ms on CPU # 120ms on GPU
        if len(rects) == 0:
            return []
        shapes = [self.shape_predictor(img_small, e) for e in rects] # 2ms
        descriptors = [self.face_recognizer.compute_face_descriptor(img_small, e) for e in shapes] # 20ms
        faces = np.vstack([preprocess(dlib_crop(img_small, e)) for e in rects])
        expressions = self.expression_classifier.run(None, {'mobilenetv2_1.00_96_input': faces})[0] # 4ms
        rects = [resize_rect(e, downsample) for e in rects]
        shapes = [resize_shape(e, downsample) for e in shapes]
        descriptors = [np.asarray(e).astype(float).tolist() for e in descriptors]
        expressions = [e.reshape(-1).astype(float) for e in expressions]
        expressions = [dict(zip(self.expression_classes, e)) for e in expressions]
        faces = []
        keys = ('rect', 'shape', 'descriptor', 'expression')
        for values in zip(rects, shapes, descriptors, expressions):
            faces.append(dict(zip(keys, values)))
        return faces