export IDS=$1
export EXPOSURE=$2
./cameras exec "cd camera && python capture-raw.py $EXPOSURE"
./cameras download /home/pi/reference/preview.jpg