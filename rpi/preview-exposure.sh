export IDS=$1
./cameras update
./cameras exec "cd camera && python capture-raw.py"
./cameras download /home/pi/reference/preview.jpg