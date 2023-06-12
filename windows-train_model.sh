#!/bin/bash
set -x
python -m venv .
./Scripts/activate.bat
cp -r ./patch ./mmsegmentation
pip install -v -e ./mmsegmentation
nohup bash tools/dist_train.sh configs/custom/<INSERT CONFIGURATION NAME HERE>.py 1 > training.log 2>&1 &
read -p "Press any key to continue"