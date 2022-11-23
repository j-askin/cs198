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
from PIL.ImageQt import ImageQt
import sys, cv2, os
import numpy as np
from PIL import Image
import time
#import torch


def pil2pixmap(im):
        #https://stackoverflow.com/questions/34697559/pil-image-to-qpixmap-conversion-issue

    if im.mode == "RGB":
        r, g, b = im.split()
        im = Image.merge("RGB", (b, g, r))
    elif  im.mode == "RGBA":
        r, g, b, a = im.split()
        im = Image.merge("RGBA", (b, g, r, a))
    elif im.mode == "L":
        im = im.convert("RGBA")
    im2 = im.convert("RGBA")
    data = im2.tobytes("raw", "RGBA")
    qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format.Format_ARGB32)
    pixmap = QtGui.QPixmap.fromImage(qim)
    return pixmap


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
    def setup_ui(self):
        self.setGeometry(0, 0, 1280, 720)
        self.setWindowTitle("CS198 Project")

        self.central_widget = QtWidgets.QWidget()

        self.image_display = QtWidgets.QScrollArea(self.central_widget)
        self.image_display.setGeometry(QtCore.QRect(0, 0, 800, 700))
        self.image_display.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.image_display.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.image_display.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
        self.image_display.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QtWidgets.QWidget(self.central_widget)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 800, 700))
        self.image_display.setWidget(self.scrollAreaWidgetContents)

        self.img_holder = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.img_holder.setGeometry(QtCore.QRect(10, 10, 500, 500))
        self.img_holder.setText("Image")
        self.img_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)


        self.output_display = QtWidgets.QTextBrowser(self.central_widget)
        self.output_display.setGeometry(QtCore.QRect(810, 10, 350, 460))

        self.change_image = QtWidgets.QPushButton(self.central_widget)
        self.change_image.setGeometry(QtCore.QRect(810, 480, 90, 30))
        self.change_image.setText("Select Image")
        self.change_image.clicked.connect(self.choose) # "Select Image" button in the app


        self.start_point_count = QtWidgets.QPushButton(self.central_widget)
        self.start_point_count.setGeometry(QtCore.QRect(910, 480, 90, 30))
        self.start_point_count.setText("Start ")
        self.start_point_count.clicked.connect(self.spc) # "Start" button in the app

        self.create_grid = QtWidgets.QPushButton(self.central_widget)
        self.create_grid.setGeometry(QtCore.QRect(1010, 480, 90, 30))
        self.create_grid.setText("Get Grid Points")
        self.create_grid.clicked.connect(self.get_points) # "Create Grid" button in the app

        self.image_text = QtWidgets.QLabel(self.central_widget)
        self.image_text.setGeometry(QtCore.QRect(810,520,400,60))
        self.image_text.setText("No image loaded")
        self.image_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)


        self.norm_img_radio = QtWidgets.QRadioButton("Normal Image", self.central_widget)
        self.norm_img_radio.setGeometry(QtCore.QRect(810, 580, 100, 30))
        self.norm_img_radio.setText("Normal Image")
        self.norm_img_radio.setChecked(True)
        self.norm_img_radio.clicked.connect(self.show_img_click)

        self.grid_img_radio = QtWidgets.QRadioButton("Grid Image", self.central_widget)
        self.grid_img_radio.setGeometry(QtCore.QRect(910, 580, 100, 30))
        self.grid_img_radio.setText("Grid Image")
        self.grid_img_radio.setChecked(False)
        self.grid_img_radio.clicked.connect(self.show_img_click)

        self.seg_img_radio = QtWidgets.QRadioButton("Segmented Image", self.central_widget)
        self.seg_img_radio.setGeometry(QtCore.QRect(1010, 580, 150, 30))
        self.seg_img_radio.setText("Segmented Image")
        self.seg_img_radio.setChecked(False)
        self.seg_img_radio.clicked.connect(self.show_img_click)

        self.disp_img_group = QtWidgets.QButtonGroup()
        self.disp_img_group.addButton(self.norm_img_radio)
        self.disp_img_group.addButton(self.grid_img_radio)
        self.disp_img_group.addButton(self.seg_img_radio)

        self.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 30))
        self.statusbar = QtWidgets.QStatusBar()

        self.lay = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents) # vertical layout box where the label goes so it can be scrollable
        self.lay.addWidget(self.img_holder) # add the label ("imgHolder") to the vertical layout box

        self.img_mode = 0
        self.show_img()

    def show_img_click(self):
        #check if a button was selected
        print(self.sender().text())
        if self.sender().text() == "Normal Image":
            self.image_text.setText(f"Displaying normal image, size: {self.img.size[0]} * {self.img.size[1]} pixels.\n{self.img_path}")
            self.img = Image.open(self.img_path)
        elif self.sender().text() == "Grid Image":
            self.image_text.setText(f"Displaying grid image, size: {self.img.size[0]} * {self.img.size[1]} pixels.\n{self.grid_img_path}")
            self.img = Image.open(self.grid_img_path)
        elif self.sender().text() == "Segmented Image":
            self.image_text.setText(f"Displaying segmented image, size: {self.img.size[0]} * {self.img.size[1]} pixels.\n{self.seg_img_path}")
            self.img = Image.open(self.seg_img_path)
        else:
            self.image_text.setText(f"Unable to display image.")
            self.img = init_img()
        self.show_img()

    def show_img(self):
        try:
            self.img_holder.setPixmap(pil2pixmap(self.img))
        except:
                self.img = init_img()
                self.img_holder.setPixmap(pil2pixmap(self.img))

    def choose(self):

        # currently only accepting PNG files, but can be changed in the future just in case
        fname = QtWidgets.QFileDialog.getOpenFileName(self, "Select Non-Grid Image", "", "PNG/JPG Files (*.jpg *.png)")
        try:
            if fname[0]: #check if filepath exists
                self.img_path = fname[0] #set image path to given file path
                self.seg_img_path = fname[0][:-4]+"_seg"+fname[0][-4:]
                self.grid_img_path = fname[0][:-4]+"_grid"+fname[0][-4:]
                self.img_mode = 0
                self.img = Image.open(self.img_path)
            else:
                raise Exception
        except:
            self.image_text.setText(f"Unable to display image.")
            self.img_path = ""
            self.img = init_img()
        finally:
            self.show_img()


    def get_points(self):
        grid_colorl = np.array((90,200,200)) #grid color in RGB format
        grid_coloru = np.array((100,255,255)) #grid color in RGB format
        pt_rad = 25 #radius of drawn points
        out_path = os.path.join(os.getcwd(),time.strftime("%m%y%d-%H%M%S",time.localtime(time.time())))
        while os.path.exists(out_path):
            out_path = out_path+"_"
        os.mkdir(out_path)
        pt_path = os.path.join(out_path,"points")
        while os.path.exists(pt_path):
            pt_path = pt_path+"_"
        os.mkdir(pt_path)
        cv_img = cv2.imread(self.grid_img_path)
        img_l,img_w = cv_img.shape[0],cv_img.shape[1]
        hsv_img = cv2.cvtColor(cv_img,cv2.COLOR_BGR2HSV)
        mask_img = cv2.inRange(hsv_img,grid_colorl,grid_coloru)
        cv2.imwrite(os.path.join(out_path,"hsv.png"),hsv_img)
        cv2.imwrite(os.path.join(out_path,"mask.png"),mask_img)
        im_cv = cv2.bitwise_and(hsv_img,hsv_img,mask=mask_img)
        cv2.imwrite(os.path.join(out_path,"Filter.png"),im_cv)
        im_g = cv2.cvtColor(im_cv,cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(im_g, 50, 200, None, 3)
        cv2.imwrite("edge.png",edges)
        lines = cv2.HoughLines(edges, 3, np.pi/2, 500)
        h_lines, v_lines = [],[]
        for line in lines:
            print(line)
            rho = line[0][0]
            theta = line[0][1]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = rho*np.cos(theta)
            y0 = rho*np.sin(theta)
            pt1 = (int(x0 + img_w*(-b)), int(y0 + img_l*(a)))
            pt2 = (int(x0 - img_w*(-b)), int(y0 - img_l*(a)))
            if theta == 0:
                h_lines.append(pt1)
            else:
                v_lines.append(pt2)
            cv2.line(im_cv, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
        for h in range(len(h_lines)):
            for v in range(len(v_lines)):
                cv2.circle(im_cv, (h_lines[h][0],v_lines[v][1]),5,(255,0,0),thickness = 5)
                cv2.circle(cv_img, (h_lines[h][0],v_lines[v][1]),25,(255,0,0),thickness = 1)
                r1=h_lines[h][0]-pt_rad
                r2=h_lines[h][0]+pt_rad
                r3=v_lines[v][1]-pt_rad
                r4=v_lines[v][1]+pt_rad
                im_pt = cv_img[r3:r4,r1:r2]
                cv2.imwrite(os.path.join(pt_path,f"({h_lines[h][0]},{v_lines[v][1]})_{h}_{v}_{50}.png"),im_pt)
        cv2.imwrite(os.path.join(out_path,"output_grid.png"),im_cv)
        cv2.imwrite(os.path.join(out_path,"output.png"),cv_img)





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

