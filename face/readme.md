# Face Analysis

First download the models:

```
bash download-models.sh
```

## Setup environment

With Anaconda:

```
conda create -y --name vibe-check-face --no-default-packages python=3.7
conda activate vibe-check-face
conda install -y opencv numpy scipy
conda install -y -c conda-forge dlib
pip install onnx onnxruntime easydict scikit-image sklearn flask pymongo
```

Or from the yml file:

```
conda env create -f environment.yml
conda activate vibe-check-app
python app.py
```

## Install CUDA

First install the NVIDIA Driver 440.100, then install CUDA:

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
sudo apt install libcudnn7 libcudnn7-dev
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
conda install opencv
pip install flask onnxruntime
```

## Building the blocklist

First, set `require_two_faces = False` in `AnalysisProcess.py` and record 100+ images from each camera in the mostly empty exhibition space.

Then run `python build-blocklist.py`. This will recognize clusters of faces based on landmarks and face descriptors. If it isn't recognizing some of the faces, lower `min_samples`. When it is done, it will output `blocklist.pkl`. This is loaded by `AnalysisProcess` to identify faces that need to be blocked.

When you are done, set `require_two_faces = True`, drop the "raw" collection and clear the images.