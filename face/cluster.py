from pymongo import MongoClient
import hdbscan

# connect to mongo
client = MongoClient()

# load all data from "raw" collection 
raw_data = []
descriptors = []
# todo: only get the 10k most recent
# https://stackoverflow.com/questions/4421207/how-to-get-the-last-n-records-in-mongodb
for e in client.vibecheck.raw.find({}):
    raw_data.append(e)
    descriptors.extend([face['descriptor'] for face in e['faces']])

# cluster all the labels (can take 15 seconds)
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=2,
    cluster_selection_epsilon=0.4,
    core_dist_n_jobs=-1)
labels = clusterer.fit_predict(descriptors)

# combine labels with raw to create recognized_photos
recognized_photos = []
labels_iter = iter(labels)
for e in raw_data:
    people = []
    for face in e['faces']:
        face_id = next(labels_iter)
        people.append({
            'faceid': str(face_id),
            'rect': face['rect'],
            'expressions': face['expression']
        })
    recognized_photos.append({
        'created': e['_id'].generation_time,
        'camera': e['camera_id'],
        'photoPath': e['photo_path'],
        'people': people
    })

# drop old recognized-photos and create a new one
client.vibecheck['recognized-photos'].drop()
client.vibecheck['recognized-photos'].insert_many(recognized_photos)