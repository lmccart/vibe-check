import os
import time
import datetime
import threading

import cv2
from flask import Flask, request, send_from_directory, jsonify
from flask_pymongo import PyMongo

from FaceAnalyzer import FaceAnalyzer, xywh_to_tblr
from draw_shapes import draw_circle, draw_rectangle, draw_text
from imutil import imread, imwrite, imdecode

preview_only = False
# preview_only = True

image_dir = '../app/images'
os.makedirs(image_dir, exist_ok=True)

# debug_dir = 'data/debug'
debug_dir = None
if debug_dir is not None:
    os.makedirs(debug_dir, exist_ok=True)

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/vibecheck'
mongo = PyMongo(app)
# mongo = None

analyzer = FaceAnalyzer()

@app.route('/vibecheck')
def root():
    return jsonify({'status': 'ok'})

@app.route('/vibecheck/download/<image>')
def download(image):
    return send_from_directory(image_dir, image)

# this should be re-designed to return immediately
# the camera should wait for the result of the detection
# instead this should pass off to a queue for analysis
# or we should switch from HTTP to ZMQ with a PUB-SUB pattern
# or with PUSH-PULL and two workers, one on each GPU
@app.route('/vibecheck/upload/<camera_id>', methods=['POST'])
def upload(camera_id):
    now = datetime.datetime.now().isoformat()
    print(now, threading.get_ident(), camera_id)

    data = request.get_data() # get bytes from request

    if preview_only:
        with open(f'data/images/{camera_id}.jpg', 'wb') as f:
            f.write(data)
        return jsonify({})

    # # read placeholder from disk
    # with open('../app/images/0.jpg', 'rb') as f:
    #     data = f.read()

    img = imdecode(data) # decode jpg to numpy
    faces = analyzer(img)

    # draw debug output on top of image
    if debug_dir is not None:
        canvas = img.copy()
        for face in faces:
            rect = xywh_to_tblr(face['rect'])
            rect = list(map(int, rect))
            draw_rectangle(canvas, rect, stroke=255)
            for point in face['shape']:
                draw_circle(canvas, point, r=4, fill=(255,255,255))
            expression = max(face['expression'], key=face['expression'].get)
            text = f"{face['expression'][expression]*100:0.0f}% {expression}"
            draw_text(canvas, text, (rect[2], rect[1]), scale=1, highlight=0,
                color=(255,255,255), thickness=2, antialias=True)
        imwrite(os.path.join(debug_dir, f'{camera_id}.jpg'), canvas)

    # only save photos where there are 2 or more people
    # otherwise we cannot analyze any relationships 
    if len(faces) >= 2:
        # save the image to disk
        millis = int(time.time() * 1000)
        fn = os.path.join(camera_id, str(millis) + '.jpg')
        os.makedirs(os.path.join(image_dir, camera_id), exist_ok=True)
        # print('saving to', fn)
        full_path = os.path.join(image_dir, fn)
        with open(full_path, 'wb') as f:
            f.write(data)
        
        if mongo is not None:
            # write analysis to db
            record = {
                'camera_id': camera_id,
                'photo_path': fn,
                'faces': faces
            }
            print('writing to db', repr(record)[:120], '...')
            mongo.db['raw'].insert_one(record)

    return jsonify(faces)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)