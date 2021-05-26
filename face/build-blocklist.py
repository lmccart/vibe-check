from pymongo import MongoClient
import numpy as np
from sklearn.cluster import DBSCAN
from collections import defaultdict
import pickle
from blocking import face_to_features

camera_count = 12
min_samples = 20
max_features = 1000

client = MongoClient()
blocklist = defaultdict(list)

for camera_id in range(camera_count):
    print(f'analyzing camera {camera_id}')
    
    features = []
    for e in client.vibecheck.raw.find({'camera_id': str(camera_id)}):
        for face in e['faces']:
            features.append(face_to_features(face))
            
    print(f'  face features: {len(features)}')
    if len(features) == 0:
        print('  skipping...')
        continue

    if len(features) > max_features:
        np.random.shuffle(features)
        features = features[:max_features]
        print(f'  limited features: {max_features}')
            
    features = np.asarray(features)
    clusterer = DBSCAN(min_samples=min_samples)
    labels = clusterer.fit_predict(features)
    unique = np.unique(labels[labels != -1])
    
    print(f'  unique clusters: {len(unique)}')
    if len(unique) == 0:
        print('  skipping...')
        continue
    
    for label in unique:
        in_group = features[labels == label]
        out_group = features[labels != label]
        mean = in_group.mean(0)
        farthest = np.sqrt((in_group - mean) ** 2).sum(1).max()
        nearest = np.sqrt((out_group - mean) ** 2).sum(1).min()
        print('  ', label, 'farthest', round(farthest,2), 'nearest', round(nearest, 2))
        
        blocklist[str(camera_id)].append(mean)

with open('blocklist.pkl', 'wb') as f:
    pickle.dump(dict(blocklist), f)
