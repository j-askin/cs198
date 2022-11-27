import PyQt5.QtWidgets as qtw
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from grid import Grid
import sys, os, cv2, time
from PIL import Image, ImageDraw
import numpy as np


class UI(qtw.QMainWindow):
    # the paths of the images to be used for point counting
    img, gridimg, segimg = "","",""
    
    isGridPresent = False
    def __init__(self):
        super(UI, self).__init__()

        # prog.ui contains the layout of the app resulting from Qt Designer
        uic.loadUi("prog.ui", self)

        #notification popup
        self.notif = qtw.QMessageBox()

        # "Select Image" button in the app
        self.changeImage.clicked.connect(self.choose)

        #Use Miguel's implementation
        self.createGrid.setText("Get Points")
        self.createGrid.clicked.connect(self.get_points)

        # Connect radio buttons to load images
        self.normImageRadio.clicked.connect(self.radio_image)
        self.gridImageRadio.clicked.connect(self.radio_image)
        self.segImageRadio.clicked.connect(self.radio_image)


        self.scene = qtw.QGraphicsScene()
        self.horizontalSlider.hide()
        self.verticalSlider.hide()
        self.gridLabel = qtw.QLabel()
        self.gridLabel.hide()

        self.show()

    def choose(self):
        # currently only accepting PNG files, but can be changed in the future just in case
        fname = qtw.QFileDialog.getOpenFileName(self, "Select Non-Grid Image", "", "PNG/JPG Files (*.jpg *.png)")
        # fname[0] is the filepath
        if fname[0]:
            self.img = fname[0]
            self.normImageRadio.setEnabled(True)
        else:
            self.img = ""
            self.normImageRadio.setEnabled(False)
            return
        
        #attempt to load the other image paths
        if os.path.exists(fname[0][:-4]+"_grid"+fname[0][-4:]):
            self.gridimg = fname[0][:-4]+"_grid"+fname[0][-4:]
            self.gridImageRadio.setEnabled(True)
        else:
            fname = qtw.QFileDialog.getOpenFileName(self, "Select Grid Image", "", "PNG/JPG Files (*.jpg *.png)")
            if fname[0]:
                self.gridimg = fname[0]
                self.gridImageRadio.setEnabled(True)
            else:
                self.normImageRadio.setEnabled(False)
                self.gridimg = ""
        if os.path.exists(fname[0][:-4]+"_seg"+fname[0][-4:]):
            self.segimg = fname[0][:-4]+"_seg"+fname[0][-4:]
            self.segImageRadio.setEnabled(True)
        else:
            fname = qtw.QFileDialog.getOpenFileName(self, "Select Segmented Image", "", "PNG/JPG Files (*.jpg *.png)")
            if fname[0]:
                self.segimg = fname[0]
                self.segImageRadio.setEnabled(True)
            else:
                self.normImageRadio.setEnabled(False)
                self.segimg = ""

        self.show_image(self.img)

    def radio_image(self):
        if self.sender().text() == "Normal Image":
            self.show_image(self.img)
        elif self.sender().text() == "Grid Image":
            self.show_image(self.gridimg)
        elif self.sender().text() == "Segmented Image":
            self.show_image(self.segimg)
        else:
            self.image_text.setText(f"Unable to display image.")

    def show_image(self,img):
        self.imageText.clear()
        self.imageText.setAutoFillBackground(False)
        #check if path to image exists
        if len(img) == 0:
            self.imageText.setText("Unable to load image.\nPlease reload all images.")
            return

        self.sample = QPixmap(img)
        rgb_image = Image.open(img).convert("RGB")

        # resize the image
        x, y = rgb_image.size
        x2 = 971 if x < 971 else x
        y2 = 631 if y < 631 else y

        self.imageDisplay.setScene(self.scene)
        self.imageDisplay.setSceneRect(0, 0, x2, y2)
        self.scene.addPixmap(self.sample)

        # displaying the size of the image
        self.imageText.setText(f"Loaded {img.split('/')[-1]}: {x} by {y} pixels")

    def get_points(self):

        #set boundaries for grid color in HSV format
        grid_colorl = np.array((90,200,200))
        grid_coloru = np.array((100,255,255))
        pt_rad = 25 #radius of drawn points

        #generate output directory
        savePath = os.path.join(os.path.expanduser("~"),f"Desktop/SoPIA/cs198/save/{time.strftime('%m%y%d-%H%M%S',time.localtime(time.time()))}")
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        pt_path = os.path.join(savePath,"points")
        if not os.path.exists(pt_path):
            os.makedirs(pt_path)

        #load images
        if len(self.img) == 0:
            self.imageText.setText("No image found.")
            return
        if len(self.gridimg) == 0:
            self.imageText.setText("No grid image found.")
            return
        cv_img = cv2.imread(self.img)
        cv_gridimg = cv2.imread(self.gridimg)
        if cv_gridimg.shape != cv_img.shape:
            self.imageText.setText("Image sizes do not match.")
            return
        img_l,img_w = cv_gridimg.shape[0],cv_img.shape[1]
        hsv_img = cv2.cvtColor(cv_gridimg,cv2.COLOR_BGR2HSV)
        mask_img = cv2.inRange(hsv_img,grid_colorl,grid_coloru)
        cv2.imwrite(os.path.join(savePath,"hsv.png"),hsv_img)
        cv2.imwrite(os.path.join(savePath,"mask.png"),mask_img)
        im_cv = cv2.bitwise_and(hsv_img,hsv_img,mask=mask_img)
        cv2.imwrite(os.path.join(savePath,"Filter.png"),im_cv)
        im_g = cv2.cvtColor(im_cv,cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(im_g, 50, 200, None, apertureSize=3)
        cv2.imwrite(os.path.join(savePath,"edge.png"),edges)
        lines = cv2.HoughLines(edges, 3, np.pi/180, 500)
        h_lines, v_lines = [],[]
        for line in lines:
            # print(line)
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
        h_lines.sort(key=lambda x: x[0])
        v_lines.sort(key=lambda x: x[1])
        coords = ""
        blank_mask = np.zeros((50,50,3), np.uint8)
        cv2.circle(blank_mask, (25,25),25,(255,255,255),thickness = -1)
        for h in range(len(h_lines)):
            for v in range(len(v_lines)):
                coords += f"({h}, {v})  ({h_lines[h][0]}, {v_lines[v][1]})\n"
                cv2.circle(im_cv, (h_lines[h][0],v_lines[v][1]),5,(255,0,0),thickness = 5)
                cv2.circle(cv_gridimg, (h_lines[h][0],v_lines[v][1]),25,(0,255,0),thickness = 2)
                r1=h_lines[h][0]-pt_rad
                r2=h_lines[h][0]+pt_rad
                r3=v_lines[v][1]-pt_rad
                r4=v_lines[v][1]+pt_rad
                temp = cv2.cvtColor(cv_img[r3:r4,r1:r2], cv2.COLOR_BGR2BGRA)
                temp[:, :, 3] = blank_mask[:,:,0]
                cv2.imwrite(os.path.join(pt_path,f"{os.path.split(self.img)[1].split('.')[0]}_({h},{v})_{h_lines[h][0]}_{v_lines[v][1]}_50.png"),temp)
        cv2.imwrite(os.path.join(savePath,"output_grid.png"),im_cv)
        cv2.imwrite(os.path.join(savePath,"output.png"),cv_gridimg)
        file = open(f"{savePath}/coordinates.txt", "w+")
        file.write(coords)
        file.close()
        self.imageText.setText(f"Points written to\n{savePath}")

app = qtw.QApplication(sys.argv)
window = UI()
app.exec_()