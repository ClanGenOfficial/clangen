#!/usr/bin/env bash

set -e # exit on failure

# cd into script location
cd "$(dirname "$0")"
poetry install --no-root
poetry run python main.py
