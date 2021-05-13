from pymongo import MongoClient
import hdbscan
import json
from bson.objectid import ObjectId

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        else:
            return obj

# connect to mongo
client = MongoClient()

def recognize():
    # load all data from "raw" collection 
    raw_data = []
    descriptors = []
    for e in client.vibecheck.raw.find().limit(10000).sort('$natural',-1):
        raw_data.append(e)
        descriptors.extend([face['descriptor'] for face in e['faces']])

    print('total descriptors:', len(descriptors))

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
    # client.vibecheck['recognized-photos'].drop()
    # client.vibecheck['recognized-photos'].insert_many(recognized_photos)

    return recognized_photos

# main method, analyzes each entry in recognized-photos, builds db of people, updates mongo
def update_db(recognized_photos):
    all_expressions = []
    people_db = {}
    
    for document in recognized_photos:
        people = document.get('people')

        # get sum of expressions in photo
        total_expressions = sum_photo_expressions(people)
        num_people = len(people) - 1
        
        # for each person, calculate total expression response
        for person in people:
            faceid = person.get('faceid')
            expressions = {}
            max_expressions = {}
            max_photos = {}
            max_rects = {}
            max_timestamp = {}
            for exp in person.get('expressions'):
                if len(all_expressions) == 0:
                    all_expressions = person.get('expressions')

                val = total_expressions[exp] - person.get('expressions')[exp]
                if exp in expressions:
                    expressions[exp] += val
                    if val > max_expressions[exp]:
                        max_expressions[exp] = val
                        max_photos[exp] = document.get('photoPath')
                        max_rects[exp] = person.get('rect')
                        max_timestamp[exp] = document.get('created')
                else:
                    expressions[exp] = val
                    max_expressions[exp] = val
                    max_photos[exp] = document.get('photoPath')
                    max_rects[exp] = person.get('rect')
                    max_timestamp[exp] = document.get('created')

            # add or update entry in people_db
            update_person_entry(people_db, faceid, expressions, max_expressions,
                max_photos, max_rects, max_timestamp, num_people)

    # enter all into mongodb
    prep_and_update_mongo(people_db)
    return all_expressions

# calculate sum expressions expressed in photo by all (helper method)
def sum_photo_expressions(people):
    total_expressions = {}
    for person in people:
        for exp in person.get('expressions'):
            val = person.get('expressions')[exp]
            if exp in total_expressions:
                total_expressions[exp] += val
            else:
                total_expressions[exp] = val
    return total_expressions

# add or update entry in people_db
def update_person_entry(people_db, faceid, expressions, max_expressions, max_photos, max_rects, max_timestamp, num_people):
    if faceid in people_db.keys():
        people_db[faceid]['num_people'] += num_people
        for exp in expressions:
            people_db[faceid]['expressions'][exp] += expressions[exp]
            if max_expressions[exp] > people_db[faceid]['max_expressions'][exp]:
                people_db[faceid]['max_expressions'][exp] = max_expressions[exp]
                people_db[faceid]['max_photos'][exp] = max_photos[exp]
                people_db[faceid]['max_rects'][exp] = max_rects[exp]
                people_db[faceid]['max_timestamp'][exp] = max_timestamp[exp]
    else:
        people_db[faceid] = {
            'expressions': expressions,
            'avg_expressions': {},
            'max_expressions': max_expressions,
            'max_photos': max_photos,
            'max_rects': max_rects,
            'max_timestamp': max_timestamp,
            'num_people': num_people,
            'faceid': faceid
        }

# calculate average expressions and update mongo
def prep_and_update_mongo(people_db):
    docs = []
    for faceid in people_db:
        for exp in people_db[faceid]['expressions']:
            people_db[faceid]['avg_expressions'][exp] = people_db[faceid]['expressions'][exp]/(people_db[faceid]['num_people'])
        docs.append(people_db[faceid])
    print('total people:', len(docs))

    client.vibecheck['people'].drop() # clear people collection, recreated regularly
    client.vibecheck['people'].insert_many(docs)

# writes json file from mongo
def write_json(all_expressions):
    output = {}
    for exp in all_expressions:
        # exp = e.get('expression')
        max_exp = client.vibecheck['people'].find().sort('avg_expressions.'+exp, -1)[0]
        output[exp] = {
            'faceid': max_exp['faceid'],
            'average': max_exp['avg_expressions'][exp],
            'photo_path': max_exp['max_photos'][exp],
            'rect': max_exp['max_rects'][exp],
            'timestamp': max_exp['max_timestamp'][exp]
        }
    with open('../app/static/data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, cls=Encoder, indent=2)

if __name__ == '__main__':
    recognized_photos = recognize()
    all_expressions = update_db(recognized_photos)
    write_json(all_expressions)

