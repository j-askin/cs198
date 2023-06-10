#!/bin/bash
set -x
python -m venv .
./Scripts/activate.bat
python -m ensurepip --upgrade
pip install -U flask pillow opencv-python numpy flask-sqlalchemy torch torchvision torchaudio openmim waitress
mim install mmengine
mim install "mmcv>=2.0.0"
git clone -b main https://github.com/open-mmlab/mmsegmentation.git
cp -r ./patch ./mmsegmentation
pip install -v -e ./mmsegmentation
read -p "Press any key to continue"