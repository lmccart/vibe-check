cd "$(dirname "$0")"
/usr/bin/python stream.py --id $1 > ~/camera.log 2>&1 &