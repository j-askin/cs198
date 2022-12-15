::Use this to package the source code to an executable.
::Make sure that python 3.8 is installed and you have at least 4GB of storage available.
:start
pip install pyinstaller
pyinstaller main_nomodel.py --add-data="sopia_ui.ui;." --onefile --noconfirm

pause