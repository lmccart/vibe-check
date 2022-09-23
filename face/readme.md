# Face Analysis

First download the models:

```
bash download-models.sh
```

## Setup environment

The `vibe-check-face` Anaconda environment is used for `database/cluster.py`, which runs regularly. `vibe-check-dlib` is needed for `vibe-check-face` service.

With Anaconda:

```
conda create -y --name vibe-check-face --no-default-packages python=3.7
conda activate vibe-check-face
conda install -y numpy scipy
pip install opencv-python onnx onnxruntime easydict scikit-image sklearn flask pymongo hdbscan
```

## Install CUDA

First install the NVIDIA Driver. This was originally tested under 515:

```
sudo apt install nvidia-driver-515
```

Then install CUDA (without the NVIDIA driver):

```
cd ~/Downloads
wget https://developer.download.nvidia.com/compute/cuda/11.7.1/local_installers/cuda_11.7.1_515.65.01_linux.run
sudo sh cuda_11.7.1_515.65.01_linux.run
```

Install cudnn with apt:

```
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub 
sudo bash -c 'echo "deb https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu2004/x86_64/ /" > /etc/apt/sources.list.d/cuda_learn.list'
sudo apt update
sudo apt install libcudnn8 libcudnn8-dev
```

## Install dlib for GPU

```
sudo apt install -y libopenblas-dev liblapack-dev cmake
conda create -y --name vibe-check-dlib --no-default-packages python=3.7
conda activate vibe-check-dlib
cd ~/Documents
git clone https://github.com/davisking/dlib.git
cd dlib && mkdir build && cd build
cmake ..
cmake --build . --config Release
sudo ldconfig
cd ..
python setup.py install --record files.txt
conda install -y numpy
pip install opencv-python flask onnxruntime pymongo
```

## Building the blocklist

First, set `require_two_faces = False` in `AnalysisProcess.py`. Then delete any old images `find app/images -type f -delete` and restart the analyzer `sudo systemctl restart vibe-check-face`. And record ~100 images from each camera in the mostly empty exhibition space. Check how many images are available with `find app/images/0 | wc -l`.

Check multiple cameras simultaneously with:

```
for id in `ls app/images/`; do echo $id `find app/images/$id | wc -l`; done
```

When enough images are available, `sudo systemctl stop vibe-check-face` then run `conda activate vibe-check-face && python build-blocklist.py`. This will recognize clusters of faces based on landmarks and face descriptors. When it is done, it will print analysis results, and output the file `blocklist.pkl`. This is loaded by `AnalysisProcess` to identify faces that need to be blocked. If it isn't recognizing some of the faces, lower `min_samples` and run again. It's ok if it's seeing some faces that aren't really there, as this will make the system more robust to pareidolic presences.

When the script is finished, set `require_two_faces = True`, drop the face-related collections:

```
mongo vibecheck -eval 'db.getCollection("raw").drop()'
mongo vibecheck -eval 'db.getCollection("people").drop()'
mongo vibecheck -eval 'db.getCollection("recognized-photos").drop()'
```

And clear the images `find app/images -type f -delete`, and restart the daemon `sudo systemctl restart vibe-check-face`.

The installation may appear broken until some people start walking through the space together.

## Taking snapshots

Delete an old snapshot to take a new snapshot.
