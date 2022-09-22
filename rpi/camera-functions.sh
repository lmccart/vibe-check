#!/bin/bash

# script configuration
HOSTNAME_PREFIX=vibe-check-camera-
HOSTNAME_SUFFIX=.local
ROOT_NAME=camera

# automatically configured global variables
SSH_FILE="$HOME/.ssh/id_rsa"
SCRIPT=`basename "$0"`
if [ -z "$IDS" ]; then
    IDS="0 1 4 5 7 9"
    # IDS="0 1 2 3 4 5 6 7 8 9 10 11"
fi

function get_hostname() {
    ID=$1
    echo $HOSTNAME_PREFIX$ID
}

function get_address() {
    ID=$1
    echo `get_hostname $ID`$HOSTNAME_SUFFIX
}

function get_at() {
    ID=$1
    ADDRESS=`get_address $ID`
    echo pi@$ADDRESS
}