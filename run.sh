#!/bin/bash

source .env
python3 bot.py --api_type "$1" --bot debug
