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
        gpu_id = os.environ['CUDA_VISIBLE_DEVICES']
        id_str = f'GPU {gpu_id}, camera {camera_id}'

        millis = int(time.time() * 1000)
        now = datetime.datetime.now().isoformat()

        start_time = time.time()
        img = imdecode(data)
        decode_duration = time.time() - start_time

        start_time = time.time()
        faces = self.analyzer(img)
        analysis_duration = time.time() - start_time

        print(id_str, round(decode_duration,3), round(analysis_duration,3), len(faces), flush=True)

        snapshot_fn = f'data/snapshot/{camera_id}.jpg'
        if not os.path.exists(snapshot_fn):
            with open(snapshot_fn, 'wb') as f:
                f.write(data)

        if len(faces) < 2:
            return

        if camera_id in ('4', '7', '8'):
            if len(faces) <= 3:
                return

        fn = os.path.join(camera_id, str(millis) + '.jpg')
        os.makedirs(os.path.join(image_dir, camera_id), exist_ok=True)
        print(id_str, 'saving to', fn, flush=True)
        full_path = os.path.join(image_dir, fn)
        with open(full_path, 'wb') as f:
            f.write(data)

        record = {
            'camera_id': camera_id,
            'photo_path': fn,
            'faces': faces
        }
        self.mongo.vibecheck.raw.insert_one(record)