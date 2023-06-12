#!/bin/bash
set -x
python -m venv .
source ./bin/activate
cp -r ./patch ./mmsegmentation
pip install -v -e ./mmsegmentation
read -p "Press any key to continue"