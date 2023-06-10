#!/bin/bash
set -x
python -m venv .
./Scripts/activate.bat
waitress-serve --host 127.0.0.1 --port 5000 app:app
read -p "Press any key to continue"