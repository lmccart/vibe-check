from markupsafe import escape
from flask import Flask, render_template, request
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/vibecheck"
mongo = PyMongo(app)

peopleDb = {}

@app.route('/')
def home_page():
  writeJson()
  return render_template('index.html') #, data=data)


# main method to be called on interval
# analyzes each entry in recognized-photos, builds db of people, updates mongo
def updateDb():
  peopleDb = {}
  
  for document in mongo.db['recognized-photos'].find({}):
    people = document.get('people')

    # get sum of expressions in photo
    totalExpressions = sumPhotoExpressions(people)
    numPeople = len(people) - 1
    
    # for each person, calculate total expression response
    for person in people:
      faceid = person.get('faceid')
      expressions = {}
      maxExpressions = {}
      maxPhotos = {}
      for exp in person.get('expressions'):
        val = totalExpressions[exp] - person.get('expressions')[exp]
        if exp in expressions:
          expressions[exp] += val
          if val > maxExpressions[exp]:
            maxExpressions[exp] = val
            maxPhotos[exp] = document.get('photoPath')
        else:
          expressions[exp] = val
          maxExpressions[exp] = val
          maxPhotos[exp] = document.get('photoPath')

      # add or update entry in peopleDb
      updatePersonEntry(faceid, expressions, maxExpressions, maxPhotos, numPeople)

  # enter all into mongodb
  prepAndUpdateMongo()

# calculate sum expressions expressed in photo by all (helper method)
def sumPhotoExpressions(people):
  totalExpressions = {}
  for person in people:
    for exp in person.get('expressions'):
      val = person.get('expressions')[exp]
      if exp in totalExpressions:
        totalExpressions[exp] += val
      else:
        totalExpressions[exp] = val
  return totalExpressions

# add or update entry in peopleDb
def updatePersonEntry(faceid, expressions, maxExpressions, maxPhotos, numPeople):
  if faceid in peopleDb.keys():
    peopleDb[faceid]['numPeople'] += numPeople
    for exp in expressions:
      peopleDb[faceid]['expressions'][exp] += expressions[exp]
      if maxExpressions[exp] > peopleDb[faceid]['maxExpressions'][exp]:
        peopleDb[faceid]['maxExpressions'][exp] = maxExpressions[exp]
        peopleDb[faceid]['maxPhotos'][exp] = maxPhotos[exp]
  else:
    peopleDb[faceid] = {
      'expressions': expressions,
      'avgExpressions': {},
      'maxExpressions': maxExpressions,
      'maxPhotos': maxPhotos,
      'numPeople': numPeople,
      'faceid': faceid
    }


# calculate average expressions and update mongo
def prepAndUpdateMongo():
  docs = []
  for faceid in peopleDb:
    for exp in peopleDb[faceid]['expressions']:
      peopleDb[faceid]['avgExpressions'][exp] = peopleDb[faceid]['expressions'][exp]/(peopleDb[faceid]['numPeople'])
    docs.append(peopleDb[faceid])
  print(len(docs))

  mongo.db['people'].drop() # clear people collection, recreated regularly
  mongo.db['people'].insert_many(docs)

# writes json file from mongo
def writeJson():
  expressions = mongo.db['meta'].find({})[0].get('expressions')
  for exp in expressions:
    print(exp)



  # expressions: {
	# neutral: { average: number, photoPath: string },
	# happiness: { average: number, photoPath: string },
	# surprise: { average: number, photoPath: string },
	# sadness: { average: number, photoPath: string },
	# anger: { average: number, photoPath: string },
	# disgust: { average: number, photoPath: string },
	# contempt: { average: number, photoPath: string },


# updateDb()
writeJson()