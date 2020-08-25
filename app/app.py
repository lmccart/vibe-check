from flask import Flask, render_template, request, jsonify, send_from_directory
from pymongo import MongoClient

app = Flask(__name__)

# connect to mongo
client = MongoClient()

@app.route('/images/<image>')
def send_image(image):
  return send_from_directory('images', image)

@app.route('/<id>')
def home_page(id):
  return render_template('index.html')

@app.route('/get_meta')
def get_meta():
  meta = client.vibecheck['meta'].find({})[0]
  del meta['_id']
  return jsonify(meta)
  
@app.route('/get_expressions')
def get_expressions():
  return jsonify(client.vibecheck['meta'].find({})[0].get('expressions'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
