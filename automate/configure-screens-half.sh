#!/bin/bash

DISPLAY=:0 xrandr \
    --output DP-2-4 --mode  1920x1080 --pos 2160x0 --rotate right -r 60 \
    --output HDMI-1 --mode  1920x1080 --pos 1080x0 --rotate right -r 60 \
    --output HDMI-1-0 --mode  1920x1080 --pos 0x0 --rotate right -r 60