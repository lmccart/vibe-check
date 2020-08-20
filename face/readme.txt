# Face Analysis

Install Python requirements:

```
conda create -n vibecheck-face python=3.7
conda activate vibecheck-face
conda install -y opencv numpy scipy
conda install -y -c conda-forge dlib
pip install onnx onnxruntime easydict scikit-image sklearn flask flask-pymongo
```

Enable .local domains under WSL:

```
sudo apt update
sudo apt install avahi-daemon avahi-utils
sudo service dbus start
sudo service avahi-daemon start
```