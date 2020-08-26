import os
import datetime
import time

from FaceAnalyzer import FaceAnalyzer
from pymongo import MongoClient
from imutil import imwrite, imdecode

image_dir = '../app/images'

class AnalysisProcess():
    def __init__(self):
        self.mongo = MongoClient()
        self.analyzer = FaceAnalyzer()

    def __call__(self, camera_id, data):
        millis = int(time.time() * 1000)
        now = datetime.datetime.now().isoformat()
        start_time = time.time()
        img = imdecode(data)
        faces = self.analyzer(img)
        duration = time.time() - start_time
        print(os.getpid(), camera_id, now, round(duration,3), len(faces))

        # with open('debug.jpg', 'wb') as f:
        #     f.write(data)

        if len(faces) < 2:
            return

        fn = os.path.join(camera_id, str(millis) + '.jpg')
        os.makedirs(os.path.join(image_dir, camera_id), exist_ok=True)
        print(os.getpid(), camera_id, 'saving to', fn)
        full_path = os.path.join(image_dir, fn)
        with open(full_path, 'wb') as f:
            f.write(data)

        record = {
            'camera_id': camera_id,
            'photo_path': fn,
            'faces': faces
        }
        self.mongo.vibecheck.raw.insert_one(record)