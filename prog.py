import PyQt5.QtWidgets as qtw
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
import sys
from PIL import Image
from grid import Grid
from error import Ui_errorMessage

class UI(qtw.QMainWindow):
    # the path of the image to be used for point counting
    img = ""   
    def __init__(self):
        super(UI, self).__init__()

        # prog.ui contains the layout of the app resulting from Qt Designer
        uic.loadUi("prog.ui", self)

        # "Select Image" button in the app
        self.changeImage.clicked.connect(self.choose)
        # "Create Grid" button in the app
        self.createGrid.clicked.connect(self.open_grid_settings)
        # "Start" button in the app
        self.startPointCount.clicked.connect(self.spc)

        # vertical layout box where the label goes so it can be scrollable
        self.lay = qtw.QVBoxLayout(self.scrollAreaWidgetContents)
        # add the label ("imgHolder") to the vertical layout box
        self.lay.addWidget(self.imgHolder)

        self.show()

    def choose(self):
        # currently only accepting PNG files, but can be changed in the future just in case
        fname = qtw.QFileDialog.getOpenFileName(self, "Select Image", "", "PNG Files (*.png)")

        # fname[0] is the filepath
        if fname[0]:
            self.img = fname[0]

        self.pixmap = QPixmap(self.img)
        # putting the image on the label
        self.imgHolder.setPixmap(self.pixmap)

        rgb_image = Image.open(self.img).convert("RGB")
        # size of the image
        x, y = rgb_image.size

        # displaying the size of the image
        self.imageSize.clear()
        self.imageSize.setText(f"Size of {self.img.split('/')[-1]}: {x} by {y} pixels")

    def open_grid_settings(self):
        if self.img:
            self.ui = Grid(self)
            self.ui.show()
        else:
            self.errorWindow = qtw.QMainWindow()
            self.ui = Ui_errorMessage()
            self.ui.setupUi(self.errorWindow)
            self.ui.errorLabel.setText("Please select an image before \ncreating a grid.")
            self.errorWindow.show()

    def spc(self):
        # if there is an image displayed
        if self.img:
            # clear the contents of the display, if any
            self.outputDisplay.clear()

            # to keep track of the number of points
            count = 1

            # get RGB values of each pixel in the image
            # this is the output for now since we have no model yet
            rgb_image = Image.open(self.img).convert("RGB")

            x, y = rgb_image.size

            # getting the (rough) interval for each point to create a 10x10 grid
            x2 = x // 11
            y2 = y // 11

            # getting those pixels/grid points and displaying their RGB value
            for i in range(x2, x-x2, x2):
                for j in range(y2, y-y2, y2):
                    r, g, b = rgb_image.getpixel((i, j))
                    self.outputDisplay.append(f"Point {count}) x: {i}, y: {j}; R: {r}, G: {g}, B: {b}")
                    count += 1

app = qtw.QApplication(sys.argv)
window = UI()
app.exec_()