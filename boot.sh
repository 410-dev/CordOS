#!/bin/bash
if [ -d "./venv" ]; then
    source ./venv/bin/activate
fi
python3 ./bootloader.py "$@"
rm -rf ./data/cache
