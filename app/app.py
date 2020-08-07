from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
import json
from bson.objectid import ObjectId

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/vibecheck'
mongo = PyMongo(app)

class Encoder(json.JSONEncoder):
  def default(self, obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, ObjectId):
      return str(obj)
    else:
      return obj




@app.route('/all0')
def all0():
  return render_template('all0.html')


@app.route('/all1')
def all1():
  return render_template('all1.html')

@app.route('/<id>')
def home_page(id):
  return render_template('index.html')

@app.route('/get_meta')
def get_meta():
  meta = mongo.db['meta'].find({})[0]
  del meta['_id']
  return jsonify(meta)
  
@app.route('/get_expressions')
def get_expressions():
  return jsonify(mongo.db['meta'].find({})[0].get('expressions'))

# main method to be called on interval
# analyzes each entry in recognized-photos, builds db of people, updates mongo
# TODO: add in timestamp
def update_db():
  people_db = {}
  
  for document in mongo.db['recognized-photos'].find({}):
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
      update_person_entry(people_db, faceid, expressions, max_expressions, max_photos, max_rects, max_timestamp, num_people)

  # enter all into mongodb
  prep_and_update_mongo(people_db)

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
  print(len(docs))

  mongo.db['people'].drop() # clear people collection, recreated regularly
  mongo.db['people'].insert_many(docs)

# writes json file from mongo
def write_json():
  expressions = mongo.db['meta'].find({})[0].get('expressions')
  output = {}
  for exp in expressions:
    max_exp = mongo.db['people'].find().sort(  'avg_expressions.'+exp, -1 )[0]
    output[exp] = { 'faceid': max_exp['faceid'], 'average': max_exp['avg_expressions'][exp], 'photo_path': max_exp['max_photos'][exp], 'rect': max_exp['max_rects'][exp], 'timestamp': max_exp['max_timestamp'][exp]}
  with open('static/data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, cls=Encoder, indent=2)


# TODO: set task to do this on interval
update_db()
write_json()


if __name__ == '__main__':
    app.run(debug=True)