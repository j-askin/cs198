#!/bin/bash
set -x
python -m venv .
./Scripts/activate.bat
cd src
waitress-serve --port 5000 app:app
read -p "Press any key to continue"