:start

pip3 install torch torchvision torchaudio
pip install -U openmim
mim install mmcv-full
pip install mmsegmentation
pip install opencv-python
python tools/train.py mmsegmentation/configs/pspnet/pspnet_r50-d8_512x1024_40k_cityscapes.py --gpu-id 0

pause