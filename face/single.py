from flask import Flask, request, jsonify

from AnalysisProcess import AnalysisProcess

app = Flask(__name__)

analyzer = AnalysisProcess()

@app.route('/vibecheck/upload/<camera_id>', methods=['POST'])
def upload(camera_id):
    data = request.get_data()
    analyzer(camera_id, data)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)