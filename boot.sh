#!/bin/bash

while true; do
    if [ -f "./restart" ]; then
        rm -f ./restart
    fi

    if [ -d "./venv" ]; then
        source ./venv/bin/activate
    fi

    if [ -f "./safe_restart" ]; then
        rm -f ./safe_restart
        python3 ./bootloader.py --safe "$@"
        exit_code=$?
    else
        python3 ./bootloader.py "$@"
        exit_code=$?
    fi

    if [ $exit_code -eq 1 ]; then
        touch ./restart
    elif [ $exit_code -eq 3 ]; then
        touch ./safe_restart
    fi

    rm -rf ./data/cache

    if [ ! -f "./restart" ]; then
        break
    fi
done
