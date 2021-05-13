from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

@app.route('/images/<camera_id>/<image>')
def send_image(camera_id, image):
  try:
    return send_from_directory(f'images/{camera_id}', image)
  except:
    return send_from_directory(f'edited/{camera_id}', image)

@app.route('/<id>')
def home_page(id):
  if id == 'all':
    return render_template('all.html')
  else:
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
