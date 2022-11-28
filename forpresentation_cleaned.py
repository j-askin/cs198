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
        border_colorl = np.array((140,110,220))
        border_coloru = np.array((160,120,255))
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

        #filter grid and borders before getting lines
        img_l,img_w = cv_img.shape[0],cv_img.shape[1]
        hsv_img = cv2.cvtColor(cv_gridimg,cv2.COLOR_BGR2HSV)
        #cv2.imwrite(os.path.join(savePath,"hsv.png"),hsv_img)
        
        bordermask_img = cv2.inRange(hsv_img,border_colorl,border_coloru)
        borderim_cv = cv2.bitwise_and(hsv_img,hsv_img,mask=bordermask_img)
        borderim_g = cv2.cvtColor(borderim_cv,cv2.COLOR_RGB2GRAY)
        borderedges = cv2.Canny(borderim_g, 50, 200, None, apertureSize=3)
        #cv2.imwrite(os.path.join(savePath,"bordermask.png"),bordermask_img)
        #cv2.imwrite(os.path.join(savePath,"Border Filter.png"),borderim_cv)
        #cv2.imwrite(os.path.join(savePath,"border.png"),borderedges)

        gridmask_img = cv2.inRange(hsv_img,grid_colorl,grid_coloru)
        gridim_cv = cv2.bitwise_and(hsv_img,hsv_img,mask=gridmask_img)
        gridim_g = cv2.cvtColor(gridim_cv,cv2.COLOR_RGB2GRAY)
        gridedges = cv2.Canny(gridim_g, 50, 200, None, apertureSize=3)
        #cv2.imwrite(os.path.join(savePath,"gridmask.png"),gridmask_img)
        #cv2.imwrite(os.path.join(savePath,"Grid Filter.png"),gridim_cv)
        #cv2.imwrite(os.path.join(savePath,"edge.png"),gridedges)

        #First hough transform: obtain locations of image borders
        lines = cv2.HoughLines(borderedges, 3, np.pi/180, 500)
        h_lines, v_lines = [],[]
        for line in lines:
            rho = line[0][0]
            theta = line[0][1]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = rho*np.cos(theta)
            y0 = rho*np.sin(theta)
            pt1 = (int(x0 + img_w*(-b)), int(y0 + img_l*(a)))
            pt2 = (int(x0 - img_w*(-b)), int(y0 - img_l*(a)))
            if theta == 0:
                h_lines.append(pt1[0])
            else:
                v_lines.append(pt2[1])
            cv2.line(borderim_cv, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
        if len(h_lines) > 0 and len(v_lines) > 0:
            xmin,xmax,ymin,ymax = min(h_lines),max(h_lines),min(v_lines),max(v_lines)
        else:
            xmin,xmax,ymin,ymax=0,img_l,0,img_w
        h_lines.sort()
        v_lines.sort()
        for h in range(len(h_lines)):
            for v in range(len(v_lines)):
                cv2.circle(borderim_cv, (h_lines[h],v_lines[v]),5,(255,0,0),thickness = 5)
                cv2.circle(cv_gridimg, (h_lines[h],v_lines[v]),25,(255,0,0),thickness = 2)
        cv2.imwrite(os.path.join(savePath,"output_border.png"),borderim_cv)

        #Second hough transform: obtain coordinates of grid intersections
        lines = cv2.HoughLines(gridedges, 3, np.pi/180, 500)
        h_lines, v_lines = [],[]
        for line in lines:
            rho = line[0][0]
            theta = line[0][1]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = rho*np.cos(theta)
            y0 = rho*np.sin(theta)
            pt1 = (int(x0 + img_w*(-b)), int(y0 + img_l*(a)))
            pt2 = (int(x0 - img_w*(-b)), int(y0 - img_l*(a)))
            if theta == 0:
                h_lines.append(pt1[0])
            else:
                v_lines.append(pt2[1])
            cv2.line(gridim_cv, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
        h_lines.sort()
        v_lines.sort()

        #Output all coordinates
        coords = ""
        blank_mask = np.zeros((pt_rad*2,pt_rad*2,3), np.uint8)
        cv2.circle(blank_mask, (pt_rad,pt_rad),pt_rad,(255,255,255),thickness = -1)
        coords += "Window Coordinates:\n"
        for h in range(len(h_lines)):
            for v in range(len(v_lines)):
                coords += f"({h}, {v})  ({h_lines[h]}, {v_lines[v]})\n"
                cv2.circle(gridim_cv, (h_lines[h],v_lines[v]),pt_rad,(255,0,0),thickness = 5)
                cv2.circle(cv_gridimg, (h_lines[h],v_lines[v]),pt_rad,(0,255,0),thickness = 2)
                r1,r2,r3,r4 =(h_lines[h]-pt_rad),(h_lines[h]+pt_rad),(v_lines[v]-pt_rad),(v_lines[v]+pt_rad)
                temp = cv2.cvtColor(cv_img[r3:r4,r1:r2], cv2.COLOR_BGR2BGRA)
                temp[:,:,3] = blank_mask[:,:,0]
                cv2.imwrite(os.path.join(pt_path,f"{os.path.split(self.img)[1].split('.')[0]}_({h},{v})_{h_lines[h]}_{v_lines[v]}_50.png"),temp)
        cv2.imwrite(os.path.join(savePath,"output_grid.png"),gridim_cv)
        cv2.imwrite(os.path.join(savePath,"output.png"),cv_gridimg)
        file = open(f"{savePath}/coordinates.txt", "w+")
        file.write(coords)
        file.close()
        self.outputDisplay.append(coords)

        #attempt to load segmented / raw image
        if len(self.segimg) != 0:
            raw_path = os.path.join(savePath,"raw")
            if not os.path.exists(raw_path):
                os.makedirs(raw_path)
            cv_segimg = cv2.imread(self.segimg)
            segimg_l,segimg_w = cv_segimg.shape[0],cv_segimg.shape[1]
            for h in range(len(h_lines)):
                h_lines[h] = int((h_lines[h]-xmin)*(segimg_w/(xmax-xmin)))
            for v in range(len(v_lines)):
                v_lines[v] = int((v_lines[v]-ymin)*(segimg_l/(ymax-ymin)))
            pt_rad = int(pt_rad*max((segimg_w/(xmax-xmin)),(segimg_l/(ymax-ymin))))
            #Output all coordinates
            coords = ""
            blank_mask = np.zeros((pt_rad*2,pt_rad*2,3), np.uint8)
            cv2.circle(blank_mask, (pt_rad,pt_rad),pt_rad,(255,255,255),thickness = -1)
            coords += "Raw Coordinates:\n"
            for h in range(len(h_lines)):
                for v in range(len(v_lines)):
                    coords += f"({h}, {v})  ({h_lines[h]}, {v_lines[v]})\n"
                    cv2.circle(cv_segimg, (h_lines[h],v_lines[v]),pt_rad,(0,255,0),thickness = 2)
                    r1,r2,r3,r4 =(h_lines[h]-pt_rad),(h_lines[h]+pt_rad),(v_lines[v]-pt_rad),(v_lines[v]+pt_rad)
                    temp = cv2.cvtColor(cv_segimg[r3:r4,r1:r2], cv2.COLOR_BGR2BGRA)
                    temp[:,:,3] = blank_mask[:,:,0]
                    cv2.imwrite(os.path.join(raw_path,f"{os.path.split(self.img)[1].split('.')[0]}_({h},{v})_{h_lines[h]}_{v_lines[v]}_50.png"),temp)
            cv2.imwrite(os.path.join(savePath,"rawoutput.png"),cv_segimg)
            file = open(f"{savePath}/rawcoordinates.txt", "w+")
            file.write(coords)
            file.close()
            self.outputDisplay.append(coords)

        self.imageText.setText(f"Points written to\n{savePath}")

app = qtw.QApplication(sys.argv)
window = UI()
app.exec_()