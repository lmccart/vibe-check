import os
import datetime
import time
import pickle

from FaceAnalyzer import FaceAnalyzer
from pymongo import MongoClient
from imutil import imwrite, imdecode
from blocking import classify

image_dir = '../app/images'
require_two_faces = True

class AnalysisProcess():
    def __init__(self):
        self.mongo = MongoClient()
        self.analyzer = FaceAnalyzer()
        self.blocklist = {}
        if os.path.exists('blocklist.pkl'):
            with open('blocklist.pkl', 'rb') as f:
                self.blocklist = pickle.load(f)

    def __call__(self, camera_id, data):
        gpu_id = os.environ['CUDA_VISIBLE_DEVICES']
        id_str = f'GPU {gpu_id}, camera {camera_id}'

        millis = int(time.time() * 1000)
        now = datetime.datetime.now().isoformat()

        start_time = time.time()
        img = imdecode(data)
        decode_duration = time.time() - start_time

        start_time = time.time()
        raw_faces = self.analyzer(img)
        analysis_duration = time.time() - start_time

        print(id_str, round(decode_duration,3), round(analysis_duration,3), len(raw_faces), flush=True)

        snapshot_fn = f'data/snapshot/{camera_id}.jpg'
        if not os.path.exists(snapshot_fn):
            os.makedirs(os.path.split(snapshot_fn)[0], exist_ok=True)
            with open(snapshot_fn, 'wb') as f:
                f.write(data)

        filtered_faces = []
        for face in raw_faces:
            if camera_id in self.blocklist and classify(face, self.blocklist[camera_id]):
                print('dropping blocked face', camera_id, flush=True)
                continue
            print('adding face', camera_id, flush=True)
            filtered_faces.append(face)

        if require_two_faces and len(filtered_faces) < 2:
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
            'faces': filtered_faces
        }
        self.mongo.vibecheck.raw.insert_one(record)