#!bin/bash

uv sync
uv lock
uv export -o dependencies.txt --no-dev
