#!/bin/bash
set -x
python -m venv .
./Scripts/activate.bat
cp -r ./patch ./mmsegmentation
pip install -v -e ./mmsegmentation
read -p "Press any key to continue"