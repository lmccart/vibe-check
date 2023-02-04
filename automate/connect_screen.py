#!/usr/bin/env python3
import subprocess
import time
import os

sleep_time = 5
count_target = 6
connect_command = './open-chrome.sh'

print('running')

def get(cmd):
    my_env = os.environ.copy()
    my_env['DISPLAY'] = ':0'
    try:
        return subprocess.check_output(cmd, env=my_env).decode('utf-8')
    except:
        return ''
    
def count_screens(xr):
    return xr.count(' connected ')

count_prev = None

while True:    
    count_cur = count_screens(get(['xrandr']))

    print('count_cur', count_cur)
    
    if count_prev != count_target and count_cur == count_target:
        print('count_target', count_target, 'connected')
        get(connect_command)
        
    count_prev = count_cur

    time.sleep(sleep_time)