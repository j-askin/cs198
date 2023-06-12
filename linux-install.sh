#!/bin/bash
set -x
python -m venv .
source ./bin/activate
python -m ensurepip --upgrade
pip install -U flask pillow opencv-python albumentations numpy flask-sqlalchemy openmim waitress
pip install -U torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
mim install mmengine
mim install "mmcv>=2.0.0"
git clone -b main https://github.com/open-mmlab/mmsegmentation.git
cp -r ./patch ./mmsegmentation
pip install -v -e ./mmsegmentation
read -p "Press any key to continue"