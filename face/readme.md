# Face Analysis

First download the models:

```
bash download-models.sh
```

## Setup environment

The `vibe-check-face` Anaconda environment is used for `cluster.py`, which runs regularly. `vibe-check-dlib` is needed for `vibe-check-face` service.

With Anaconda:

```
conda create -y --name vibe-check-face --no-default-packages python=3.7
conda activate vibe-check-face
conda install -y opencv numpy scipy
conda install -y -c conda-forge dlib
pip install onnx onnxruntime easydict scikit-image sklearn flask pymongo hdbscan
```

Or from the yml file:

```
conda env create -f environment.yml
conda activate vibe-check-app
python app.py
```

## Install CUDA

First install the NVIDIA Driver. This was originally tested under 440.100:

```
sudo apt install nvidia-driver-440
```

Then install CUDA (without the NVIDIA driver):

```
cd ~
wget https://developer.nvidia.com/compute/cuda/10.1/Prod/local_installers/cuda_10.1.105_418.39_linux.run
chmod +x cuda_10.1.105_418.39_linux.run
sudo ./cuda_10.1.105_418.39_linux.run
```

And add the path to your `~/.profile`:

```
if [ -d "/usr/local/cuda-10.1/bin/" ]; then
    export PATH=/usr/local/cuda-10.1/bin${PATH:+:${PATH}}
    export LD_LIBRARY_PATH=/usr/local/cuda-10.1/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
fi
```

Install cudnn with apt:

```
sudo apt-key adv --fetch-keys  http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
sudo bash -c 'echo "deb http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64 /" > /etc/apt/sources.list.d/cuda_learn.list'
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
conda install -y opencv
pip install flask onnxruntime pymongo
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