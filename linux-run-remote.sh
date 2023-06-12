#!/bin/bash
set -x
python -m venv .
source ./bin/activate
waitress-serve --host 127.0.0.1 --port 5000 app:src/app
read -p "Press any key to continue"