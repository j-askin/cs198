::Use this to package the source code to an executable.
::Make sure that python 3.8 is installed and you have at least 4GB of storage available.
::Adjust the --paths argument to match the location of your Python installation.
::IMPORTANT: PyTorch with cuda is not supported. Use a venv with PyTorch for CPU
:start
pip install pyinstaller
pyinstaller main.py --hidden-import=mmcv._ext --paths %USERPROFILE%\AppData\Local\Programs\Python\Python38\Lib\site-packages\PyQt5\Qt5\bin --add-data="sopia_ui.ui;." --onefile --noconfirm

pause