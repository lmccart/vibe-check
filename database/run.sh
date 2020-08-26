#!/bin/sh
min_interval=60
while true
do
    start=`date +%s`
    ~/miniconda3/envs/vibe-check-face/bin/python cluster.py
    end=`date +%s`
    duration=$((end-start))
    echo $duration" second"
    remaining=$((min_interval-duration))
    sleep $remaining
done