import os
import time
import datetime
import threading

import cv2
from flask import Flask, request, send_from_directory, jsonify
from flask_pymongo import PyMongo

from FaceAnalyzer import FaceAnalyzer
from draw_shapes import draw_circle, draw_rectangle, draw_text
from imutil import imread, imwrite

image_dir = 'data/images'
os.makedirs(image_dir, exist_ok=True)

app = Flask(__name__)

mongo = None
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/vibecheck'
# mongo = PyMongo(app)

analyzer = FaceAnalyzer()

@app.route('/vibecheck')
def root():
    return jsonify({'status': 'ok'})

@app.route('/vibecheck/download/<image>')
def download(image):
    return send_from_directory(image_dir, image)

@app.route('/vibecheck/upload/<camera_id>', methods=['POST'])
def upload(camera_id):
    millis = int(time.time() * 1000)
    fn = f'{image_dir}/{camera_id}.jpg'#-{millis}.jpg'
    data = request.get_data()

    now = datetime.datetime.now().isoformat()
    print(now, threading.get_ident(), camera_id)

    # uncomment to do nothing
    # return jsonify({'filename': fn})

    # print(len(data))
    with open(fn, 'wb') as f:
        f.write(data)

    # uncomment to only save file without analysis
    # return jsonify({'filename': fn})

    img = imread(fn)
    faces = analyzer(img)

    canvas = img.copy()
    for face in faces:
        rect = face['rect']
        draw_rectangle(canvas, rect, stroke=255)
        for point in face['shape']:
            draw_circle(canvas, point, r=4, fill=(255,255,255))
        expression = max(face['expression'], key=face['expression'].get)
        text = f"{face['expression'][expression]*100:0.0f}% {expression}"
        draw_text(canvas, text, (rect[2], rect[1]), scale=1, highlight=0,
            color=(255,255,255), thickness=2, antialias=True)
    imwrite('out.jpg', canvas)

    if mongo is not None:
        mongo.db['raw'].insert_one({
            'camera_id': camera_id,
            'photo_path': fn,
            'faces': faces
        })

    return jsonify(faces)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)