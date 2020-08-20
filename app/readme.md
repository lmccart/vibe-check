* https://flask.palletsprojects.com/en/1.1.x/installation/#installation
* https://flask-pymongo.readthedocs.io/en/latest/

With virtual environment:

```terminal
$ # start remote connection to server
$ . venv/bin/activate
$ export FLASK_APP=app.py
$ export FLASK_ENV=development # debug
$ cd app
$ python app.py
```

With Anaconda:

```terminal
$ conda create -n vibecheck-app python=3.7
$ conda activate vibecheck-app
$ pip install -r requirements.txt
$ python app.py
```