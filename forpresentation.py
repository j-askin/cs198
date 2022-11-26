import PyQt5.QtWidgets as qtw
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from grid import Grid
from error import Ui_errorMessage
import sys
from PIL import Image, ImageDraw
import cv2
import numpy as np


class UI(qtw.QMainWindow):
    # the path of the image to be used for point counting
    img = ""
    isGridPresent = False
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

        self.scene = qtw.QGraphicsScene()
        self.horizontalSlider.hide()
        self.horizontalSlider.valueChanged.connect(self.move_grid_h)
        self.verticalSlider.hide()
        self.verticalSlider.valueChanged.connect(self.move_grid_v)
        self.gridLabel = qtw.QLabel()
        self.gridLabel.hide()

        self.show()

    def choose(self):
        # currently only accepting PNG files, but can be changed in the future just in case
        fname = qtw.QFileDialog.getOpenFileName(self, "Select Image", "", "PNG Files (*.png)")

        # fname[0] is the filepath
        if fname[0]:
            self.img = fname[0]
        
        if not self.img:
            return

        self.sample = QPixmap(self.img)

        rgb_image = Image.open(self.img).convert("RGB")
        # size of the image
        x, y = rgb_image.size

        x2 = 1501 if x < 1501 else x
        y2 = 801 if y < 801 else y
        
        self.imageDisplay.setScene(self.scene)
        self.imageDisplay.setSceneRect(0, 0, x2, y2)
        self.scene.addPixmap(self.sample)

        # displaying the size of the image
        self.imageSize.clear()
        self.imageSize.setAutoFillBackground(False)
        self.imageSize.setText(f"{self.img.split('/')[-1]}: {x} by {y} pixels")

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

    def move_grid_h(self, value):
        y = self.gridLabel.y()
        self.gridLabel.move(value, y)
        return

    def move_grid_v(self, value):
        x = self.gridLabel.x()
        self.gridLabel.move(x, value)
        return

    def spc(self):
        # if there is an image displayed
        if bool(self.img) :
            # clear the contents of the display, if any
            self.outputDisplay.clear()

            # x = self.gridLabel.x()
            # y = self.gridLabel.y()
            
            img1 = Image.open(self.img)
            # img2 = Image.open("grid.png")
            temp_im = img1.copy()
            # temp_im.paste(img2, (x, y), img2)  # use img2.convert('RGBA') in case "bad transparency mask" error comes up
            temp_im.save("overlay.png", "PNG")

            x_min, y_min, x_max, y_max = self.get_hough("overlay.png", "result.png")
            self.crop(x_min, y_min, x_max, y_max, self.img, "cropped.png")
            self.scale("cropped.png", "resized.png")
            h, v = self.get_hough_2("resized.png", "detectedGrid2.png")
            src = "C:/Users/josh/Documents/School stuff/4thYr1stSem/CS 198/proj/sopia_data/SoPIA_20221017/Aggregates/SoPIA files/CRM-003-Fresh-Montalban (090919)/Sample under XPL.png"
            points = self.get_intersections(src, "intersections.png", h, v)
            self.get_images(points, src)
            self.processDone = qtw.QMainWindow()
            self.ui = Ui_errorMessage()
            self.ui.setupUi(self.processDone)
            self.processDone.setWindowTitle("Done")
            self.ui.errorLabel.setText("Process finished.")
            self.processDone.show()
        return

    def get_hough(self, path_open, path_save):
        # size = cv2.imread("grid.png").shape
        img = cv2.imread(path_open)
        # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(img,250,900,apertureSize=3)
        # cv2.imshow('edges', edges)
        lines_list =[]
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=min(500, 500), maxLineGap=30)
        for points in lines:
            x1,y1,x2,y2=points[0]
            cv2.line(img,(x1,y1),(x2,y2),(0,255,0),1)
            lines_list.append([(x1,y1),(x2,y2)])
        
        x_min = 0
        x_max = 0
        y_min = 0
        y_max = 0

        temp = sorted(lines_list, key=lambda x: x[0][0])
        for i in range(len(temp)):
            if temp[i+1][0][0] - temp[i][0][0] < 3:
                x_min = temp[i][0][0]
                break
        for i in range(len(temp)-1, -1, -1):
            if temp[i][0][0] - temp[i-1][0][0] < 3:
                x_max = temp[i][0][0]
                break
        
        temp2 = sorted(lines_list, key=lambda x: x[1][1])
        for i in range(len(temp)):
            if temp2[i+1][1][1] - temp2[i][1][1] < 3:
                y_min = temp2[i][1][1]
                break
        for i in range(len(temp)-1, -1, -1):
            if temp2[i][1][1] - temp2[i-1][1][1] < 3:
                y_max = temp2[i][1][1]
                break
        cv2.imwrite(path_save,img)
        return x_min, y_min, x_max, y_max
    
    def crop(self, x_min, y_min, x_max, y_max, path_open, path_save):
        temp = Image.open(path_open)
        image = temp.crop((x_min, y_min, x_max, y_max))
        image.save(path_save, "PNG")
        return
    
    def scale(self, path_open, path_save):
        temp = Image.open(path_open)
        image = temp.resize((1920,1200))
        image.save(path_save, "PNG")
        return
    
    def get_hough_2(self, path_open, path_save):
        # size = cv2.imread("grid.png").shape
        img = cv2.imread(path_open)
        # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(img,250,900,apertureSize=3)
        # cv2.imshow('edges', edges)

        lines = cv2.HoughLinesP(edges, 2, np.pi/180, threshold=100, minLineLength=min(500, 500), maxLineGap=50)
        
        h_new, v_new = self.clean_lines(lines)

        for points in v_new + h_new:
            x1,y1=points[0]
            x2,y2=points[1]
            cv2.line(img,(x1,y1),(x2,y2),(0,255,0),1)
        
        cv2.imwrite(path_save,img)
        return h_new, v_new

    def clean_lines(self, lines):
        h = []
        v = []
        for i in lines:
            if i[0][0] == i[0][2]:
                v.append(i)
            else:
                h.append(i)
        h.sort(key=lambda x: x[0][1])
        hlen = len(h)
        h_new = []
        while hlen > 0:
            if hlen == 1:
                h_new.append([(h[0][0][0], h[0][0][1]), (h[0][0][2], h[0][0][3])])
                break
            if h[1][0][1] - h[0][0][1] > 5:
                h_new.append([(h[0][0][0], h[0][0][1]), (h[0][0][2], h[0][0][3])])
                h.pop(0)
            else:
                if h[0][0][2] - h[0][0][0] > h[1][0][2] - h[1][0][0]:
                    h.pop(1)
                else:
                    h.pop(0)
            hlen -= 1

        v.sort(key=lambda x: x[0][0])
        vlen = len(v)
        v_new = []
        while vlen > 0:
            if vlen == 1:
                v_new.append([(v[0][0][0], v[0][0][1]), (v[0][0][2], v[0][0][3])])
                break
            if v[1][0][0] - v[0][0][0] > 5:
                v_new.append([(v[0][0][0], v[0][0][1]), (v[0][0][2], v[0][0][3])])
                v.pop(0)
            else:
                if v[0][0][1] - v[0][0][3] > v[1][0][1] - v[1][0][3]:
                    v.pop(1)
                else:
                    v.pop(0)
            vlen -= 1
        
        return h_new, v_new
    
    def get_intersections(self, path_open, path_save, h, v):
        points = []
        for i in h:
            for j in v:
                if (j[0][1] >= i[0][1] or abs(j[0][1] - i[0][1]) <= 2) and (j[1][1] <= i[0][1] or abs(j[1][1] - i[0][1]) <= 2):
                    if (i[1][0] >= j[0][0] or abs(i[1][0] - j[0][0]) <= 2) and (i[0][0] <= j[0][0] or abs(i[0][0] - j[0][0]) <= 2):
                        if j[0][0] > 50 and j[0][0] < 1870 and i[0][1] > 50 and i[0][1] < 1150:
                            points.append((j[0][0], i[0][1]))
        points.sort(key=lambda x: (x[1], x[0]))
        img_ref = cv2.imread(path_open)
        yellow = (0, 255, 255)
        for i in points:
            img_ref[i[1]][i[0]] = yellow
            img_ref[i[1]+1][i[0]] = yellow
            img_ref[i[1]-1][i[0]] = yellow
            img_ref[i[1]][i[0]+1] = yellow
            img_ref[i[1]][i[0]-1] = yellow
            img_ref[i[1]+1][i[0]+1] = yellow
            img_ref[i[1]+1][i[0]-1] = yellow
            img_ref[i[1]-1][i[0]-1] = yellow
            img_ref[i[1]-1][i[0]+1] = yellow
        cv2.imwrite(path_save, img_ref)
        return points
    
    def get_images(self, points, path_open):
        img = Image.open(path_open).convert("RGB")
        img_data = np.array(img)
        temp = Image.new('L', img.size, 0)
        circle_mask = ImageDraw.Draw(temp)
        coords = ""
        for i in range(len(points)):
            coords += f"({i%10}, {i//10})  ({points[i][0]}, {points[i][1]})\n"
            circle_mask.pieslice(((points[i][0]-25, points[i][1]-25), (points[i][0]+25, points[i][1]+25)), 0, 360, fill = 255)
            mask = np.array(temp)
            cropped = np.dstack((img_data, mask))
            circle = Image.fromarray(cropped).crop((points[i][0]-25, points[i][1]-25, points[i][0]+26, points[i][1]+26)).resize((510,510))
            circle.save(f"C:/Users/josh/Desktop/App Output/images/{path_open.split('/')[-1].split('.')[0]}_({i%10},{i//10})_{points[i][0]}_{points[i][1]}_51.png")
        file = open("C:/Users/josh/Desktop/App Output/coordinates.txt", "w+")
        file.write(coords)
        file.close()
        return

app = qtw.QApplication(sys.argv)
window = UI()
app.exec_()