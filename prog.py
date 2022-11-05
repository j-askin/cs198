# dialog box -> https://www.youtube.com/watch?v=gg5TepTc2Jg
# display image -> https://www.youtube.com/watch?v=6zkOrq9YVik

'''
Other stuff:
- panning, zooming image
- reading pixel RGB values
    - use Pillow -> https://stackoverflow.com/questions/138250/how-to-read-the-rgb-value-of-a-given-pixel-in-python
'''

import PyQt5.QtWidgets as qtw
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
import sys
from PIL import Image

class UI(qtw.QMainWindow):
    # the path of the image to be used for point counting
    img = ""   
    def __init__(self):
        super(UI, self).__init__()

        # prog.ui contains the layout of the app resulting from Qt Designer
        uic.loadUi("prog.ui", self)

        # "Select Image" button in the app
        self.changeImage.clicked.connect(self.choose)
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

            # size of the image
            x, y = rgb_image.size

            # displaying the size of the image
            self.outputDisplay.append(f"Image size: {x} by {y} pixels")

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