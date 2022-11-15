# dialog box -> https://www.youtube.com/watch?v=gg5TepTc2Jg
# display image -> https://www.youtube.com/watch?v=6zkOrq9YVik

'''
Other stuff:
- panning, zooming image
- reading pixel RGB values
    - use Pillow -> https://stackoverflow.com/questions/138250/how-to-read-the-rgb-value-of-a-given-pixel-in-python
'''

'''
convert with
https://stackoverflow.com/questions/1733096/convert-pyqt-to-pil-image
'''

from PyQt6 import QtCore, QtGui, QtWidgets

import sys
from PIL import Image, ImageQt
#import torch



def init_img(isz = 600, csz = 60):
    blimg = Image.new(mode="RGB",size=(600,600),color=(255,255,255))
    cell1 = Image.new(mode="RGB",size=(60,60),color=(0,128,255))
    cell2 = Image.new(mode="RGB",size=(60,60),color=(0,0,0))
    celluse = True
    for i in range(0,isz,csz):
        for j in range(0,isz,csz):
            blimg.paste((cell1 if celluse else cell2),(i,j))
            celluse = not celluse
        celluse = not celluse
    return blimg

class Ui_MainWindow(QtWidgets.QMainWindow):
    img = init_img()
    img_path = ""


    def img_show(self):
        self.qt_img = ImageQt.ImageQt(self.img)
        self.pixmap = QtGui.QPixmap.fromImage(self.qt_img) #set displayed image to a pixmap
        self.img_holder.setPixmap(self.pixmap) # putting the image on the label

    def setup_ui(self):
        self.setGeometry(0, 0, 1280, 720)
        self.setWindowTitle("CS198 Project")

        self.central_widget = QtWidgets.QWidget()


        self.image_display = QtWidgets.QScrollArea(self.central_widget)
        self.image_display.setGeometry(QtCore.QRect(0, 0, 600, 600))
        self.image_display.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.image_display.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.image_display.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
        self.image_display.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 600, 600))
        self.image_display.setWidget(self.scrollAreaWidgetContents)

        self.img_holder = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.img_holder.setGeometry(QtCore.QRect(10, 10, 500, 500))
        self.img_holder.setText("Image")
        self.img_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.img_show()

        self.output_display = QtWidgets.QTextBrowser(self.central_widget)
        self.output_display.setGeometry(QtCore.QRect(610, 10, 350, 460))

        self.change_image = QtWidgets.QPushButton(self.central_widget)
        self.change_image.setGeometry(QtCore.QRect(620, 480, 90, 30))
        self.change_image.setText("Select Image")
        self.change_image.clicked.connect(self.choose) # "Select Image" button in the app


        self.start_point_count = QtWidgets.QPushButton(self.central_widget)
        self.start_point_count.setGeometry(QtCore.QRect(720, 480, 90, 30))
        self.start_point_count.setText("Start ")
        self.start_point_count.clicked.connect(self.spc) # "Start" button in the app

        self.grid_toggle = QtWidgets.QRadioButton(self.central_widget)
        self.grid_toggle.setGeometry(QtCore.QRect(820,480,90,30))
        self.grid_toggle.setText("Show Grid")
        self.grid_toggle.clicked.connect(self.show_grid)

        self.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 30))
        self.statusbar = QtWidgets.QStatusBar()

        self.lay = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents) # vertical layout box where the label goes so it can be scrollable
        self.lay.addWidget(self.img_holder) # add the label ("imgHolder") to the vertical layout box

    def choose(self):

        # currently only accepting PNG files, but can be changed in the future just in case
        fname = QtWidgets.QFileDialog.getOpenFileName(self, "Select Image", "", "PNG Files (*.png)")
        try:
            if fname[0]: #check if filepath exists
                self.img_path = fname[0] #set image path to given file path
                self.img = Image.open(self.img_path)
        except:
            print("Unable to open image.")
            self.img_path = ""
            self.img = init_img()
        self.img_show()


    def draw_grid(self):
        self.output_display.clear()

        pass

    def show_grid(self):
        pass

    def spc(self):
    
        # clear the contents of the display, if any
        self.output_display.clear()

        # to keep track of the number of points
        count = 1

        # get RGB values of each pixel in the image
        # this is the output for now since we have no model yet
        rgb_image = self.img.convert("RGB")

        # size of the image
        x, y = rgb_image.size

        # displaying the size of the image
        self.output_display.append(f"Image size: {x} by {y} pixels")

        # getting the (rough) interval for each point to create a 10x10 grid
        x2 = x // 11
        y2 = y // 11

        # getting those pixels/grid points and displaying their RGB value
        for i in range(x2, x-x2, x2):
            for j in range(y2, y-y2, y2):
                r, g, b = rgb_image.getpixel((i, j))
                self.output_display.append(f"Point {count}) x: {i}, y: {j}; R: {r}, G: {g}, B: {b}")
                count += 1


    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setup_ui()
        self.show() #show the UI window


app = QtWidgets.QApplication(sys.argv)
window = Ui_MainWindow()
window.show()
sys.exit(app.exec())

