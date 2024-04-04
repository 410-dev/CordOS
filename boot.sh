#!/bin/bash

while true; do
    if [ -f "./restart" ]; then
        rm -f ./restart
    fi

    if [ -d "./venv" ]; then
        source ./venv/bin/activate
    fi

    python3 ./bootloader.py "$@"

    rm -rf ./data/cache

    if [ ! -f "./restart" ]; then
        break
    fi
done
