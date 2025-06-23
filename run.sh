#!/usr/bin/env bash

set -e # exit on failure

# cd into script location
cd "$(dirname "$0")"
uv sync
uv run main.py
