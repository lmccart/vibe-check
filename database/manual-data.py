from pymongo import MongoClient
import hdbscan
import json
from bson.objectid import ObjectId
from cluster import write_json

# connect to mongo
client = MongoClient()

targets = {
    'neutral':'4/1598376764645.jpg',
    'happiness':'4/1598376764645.jpg',
    'surprise':'4/1598376764645.jpg',
    'anger':'4/1598376764645.jpg',
    'disgust':'4/1598376764645.jpg',
    'fear':'4/1598376764645.jpg',
    'contempt':'4/1598376764645.jpg'
}

results = {}
for key,fn in targets.items():
    data = client.vibecheck.raw.find({'photo_path':fn}).limit(1)[0]
    results[key] = {
        'faceid': 0,
        'average': 1.0,
        'photo_path': fn,
        'rect': data['faces'][0]['rect'],
        'timestamp': data['_id'].generation_time
    }

write_json(results)