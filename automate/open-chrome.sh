#!/usr/bin/env bash

cd ~/Documents/vibe-check/automate

killall chrome
DISPLAY=:0.0 ./multibrowse \
    http://localhost:8080/0 \
    http://localhost:8080/1 \
    http://localhost:8080/2
DISPLAY=:0.1 ./multibrowse \
    http://localhost:8080/3 \
    http://localhost:8080/4 \
    http://localhost:8080/5