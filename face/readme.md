# Face Analysis

With Anaconda:

```
conda create -y --name vibe-check-face --no-default-packages python=3.7
conda activate vibe-check-face
conda install -y opencv numpy scipy
conda install -y -c conda-forge dlib
pip install onnx onnxruntime easydict scikit-image sklearn flask flask-pymongo
```

Or from the yml file:

```
$ conda env create -f environment.yml
$ conda activate vibe-check-app
$ python app.py
```

## On Windows

Enable .local domains under WSL:

```
sudo apt update
sudo apt install avahi-daemon avahi-utils
sudo service dbus start
sudo service avahi-daemon start
```
