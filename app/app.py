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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
