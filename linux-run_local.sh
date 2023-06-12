#!/bin/bash
set -x
python -m venv .
source ./bin/activate
flask --app ./src/app.py run --debug
read -p "Press any key to continue"