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
        # "Create Grid" button in the app
        #self.createGrid.clicked.connect(self.open_grid_settings)
        # "Start" button in the app
        self.startPointCount.clicked.connect(self.spc)

        #Use Miguel's implementation
        self.createGrid.setText("Get Points")
        self.createGrid.clicked.connect(self.get_points)

        # Connect radio buttons to load images
        self.normImageRadio.clicked.connect(self.radio_image)
        self.gridImageRadio.clicked.connect(self.radio_image)
        self.segImageRadio.clicked.connect(self.radio_image)


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

    def open_grid_settings(self):
        if self.img:
            self.ui = Grid(self)
            self.ui.show()
        else:
            self.notif.setIcon(qtw.QMessageBox.Critical)
            self.notif.setText("Please select an image before creating a grid.")
            self.notif.setWindowTitle("Error")
            self.notif.exec()

    def move_grid_h(self, value):
        y = self.gridLabel.y()
        self.gridLabel.move(value, y)
        return

    def move_grid_v(self, value):
        x = self.gridLabel.x()
        self.gridLabel.move(x, value)
        return

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

    def spc(self):
        # if there is an image displayed
        if bool(self.img):
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
            src = os.path.join(os.path.join(os.path.expanduser("~"),"Desktop/SoPIA/cs198/demo/test_grid.png"))
            points = self.get_intersections(src, "intersections.png", h, v)
            self.get_images(points, src)
            self.notif = qtw.QMessageBox()
            self.notif.setIcon(qtw.QMessageBox.Information)
            self.notif.setText("Obtained grid points.")
            self.notif.setWindowTitle("Done")
            self.notif.exec()

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
        savePath = os.path.join(os.path.expanduser("~"),f"Desktop/SoPIA/cs198/save/{time.strftime('%m%y%d-%H%M%S',time.localtime(time.time()))}")
        if not os.path.exists(savePath):
            os.makedirs(savePath)
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
            
            circle.save(f"{savePath}{os.path.split(self.img)[1].split('.')[0]}_({i%10},{i//10})_{points[i][0]}_{points[i][1]}_51.png")
        file = open(f"{savePath}coordinates.txt", "w+")
        file.write(coords)
        file.close()
        return

app = qtw.QApplication(sys.argv)
window = UI()
app.exec_()