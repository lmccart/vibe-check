import numpy as np

def face_to_features(face):
    shape = np.asarray(face['shape']).astype(float)
    descriptor = np.asarray(face['descriptor']).astype(float)
    # 1/320 is approximately (128/10)/4096
    # 128 = len(descriptor), 10 = len(shape), 4096 = max(shape)
    position_weight = 1/320
    features = np.hstack((shape.reshape(-1) * position_weight, descriptor))
    return features
    
def classify(face, blocklist, threshold=8):
    features = face_to_features(face)
    distances = np.sqrt((features - np.asarray(blocklist)) ** 2).sum(1)
    closest = distances.min()
    return closest < threshold