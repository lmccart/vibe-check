mkdir -p models
cd models

for DLIB_FN in shape_predictor_5_face_landmarks dlib_face_recognition_resnet_model_v1; do
    wget http://dlib.net/files/$DLIB_FN.dat.bz2
    bzip2 -d $DLIB_FN.dat.bz2
done

wget https://storage.googleapis.com/vibe-check-installation/models/ferplus-mobilenetv2-0.830.onnx
wget https://storage.googleapis.com/vibe-check-installation/models/ferplus_classes.txt