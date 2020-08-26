# Frontend Server

* https://flask.palletsprojects.com/en/1.1.x/installation/#installation
* https://flask-pymongo.readthedocs.io/en/latest/

With virtual environment:

```
. venv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=development # debug
cd app
python app.py
```

With Anaconda:

```
conda create -y --name vibe-check-app --no-default-packages python=3.7
conda activate vibe-check-app
conda install -y flask==1.1.2
python app.py
```

Or from the yml file:

```
conda env create -f environment.yml
conda activate vibe-check-app
python app.py
```