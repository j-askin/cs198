::Use this to automatically install dependencies.
::Make sure that python 3.8 and pip are installed and you have a stable unlimited internet connection.
::CPU-only version is installed by default. For GPU version, use
::--paths C:\Users\MYUSERNAME\AppData\Local\Programs\Python\Python35-32\Lib\site-packages\PyQt5\Qt\bin
:start
pip install flask opencv-python numpy pillow
pip install torch torchvision torchaudio
pip install -U openmim
mim install mmcv-full
cd "%USERPROFILE%\Desktop\SoPIA\mmsegmentation"
pip install -v -e .
cd "%USERPROFILE%\Desktop\SoPIA\mmclassification"
pip install -v -e .
pause