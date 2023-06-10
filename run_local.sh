#!/bin/bash
set -x
python -m venv .
./Scripts/activate.bat
flask --app ./app.py run --debug
read -p "Press any key to continue"