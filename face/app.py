from multiprocessing import Process
from multiprocessing.managers import BaseManager
from queue import Queue
import time
import os

from flask import Flask, request, jsonify

class MyManager(BaseManager):
    pass

class Tracker():
    def __init__(self):
        self.running = True

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

MyManager.register('Queue', Queue)
MyManager.register('Tracker', Tracker)

manager = MyManager()
manager.start()
queue = manager.Queue(maxsize=16)
tracker = manager.Tracker()

def run(gpu_id, queue, tracker):
    os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
    from AnalysisProcess import AnalysisProcess
    analyzer = AnalysisProcess()
    while tracker.is_running():
        analyzer(*queue.get())
        print('gpu', gpu_id)

processes = []

gpu_count = 2
for gpu_id in range(gpu_count):
    p = Process(target=run, args=[gpu_id, queue, tracker])
    p.start()
    processes.append(p)

app = Flask(__name__)

@app.route('/vibecheck/upload/<camera_id>', methods=['POST'])
def upload(camera_id):
    queue.put_nowait((camera_id, request.get_data()))
    return jsonify(success=True)

try:
    app.run(host='0.0.0.0', debug=True)
except:
    pass

tracker.stop()
for p in processes:
    p.join()
manager.shutdown()