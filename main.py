import PyQt5.QtWidgets as qtw
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
import sys, os, cv2, time
from PIL import Image
import numpy as np


class UI(qtw.QMainWindow):
    # the paths of the images to be used for point counting
    img, gridimg, segimg,  = "","",""
    # paths for model config and weights
    cfg, mdl, pth = "", "", ""
    t_buttonstate = [True,True,True,True]
    t_radiostate = [False,False,False]
    
    def __init__(self):
        super(UI, self).__init__()

        # prog.ui contains the layout of the app resulting from Qt Designer
        uic.loadUi("sopia_ui.ui", self)

        #notification popup
        self.notif = qtw.QMessageBox()

        # "Assign functions to buttons"
        self.loadImage.clicked.connect(self.load_image)
        self.loadModel.clicked.connect(self.load_model)
        self.segmentImage.clicked.connect(self.segment_image)
        self.getPoints.clicked.connect(self.get_points)

        # Connect radio buttons to load images
        self.normImageRadio.clicked.connect(self.radio_image)
        self.gridImageRadio.clicked.connect(self.radio_image)
        self.segImageRadio.clicked.connect(self.radio_image)

        self.scene = qtw.QGraphicsScene()
        self.gridLabel = qtw.QLabel()
        self.gridLabel.hide()
        self.show()

    def lock_ui(self):
        self.t_buttonstate = [self.loadImage.isEnabled(),self.loadModel.isEnabled(),self.segmentImage.isEnabled(),self.getPoints.isEnabled()]
        self.t_radiostate = [self.normImageRadio.isEnabled(),self.gridImageRadio.isEnabled(),self.segImageRadio.isEnabled()]
        self.loadImage.setEnabled(False)
        self.loadModel.setEnabled(False)
        self.segmentImage.setEnabled(False)
        self.getPoints.setEnabled(False)
        self.normImageRadio.setEnabled(False)
        self.gridImageRadio.setEnabled(False)
        self.segImageRadio.setEnabled(False)

    def unlock_ui(self):
        self.loadImage.setEnabled(self.t_buttonstate[0])
        self.loadModel.setEnabled(self.t_buttonstate[1])
        self.segmentImage.setEnabled(self.t_buttonstate[2])
        self.getPoints.setEnabled(self.t_buttonstate[3])
        self.normImageRadio.setEnabled(self.t_radiostate[0])
        self.gridImageRadio.setEnabled(self.t_radiostate[1])
        self.segImageRadio.setEnabled(self.t_radiostate[2])


    def load_image(self):
        self.lock_ui()
        # currently only accepting PNG files, but can be changed in the future just in case
        fname = qtw.QFileDialog.getOpenFileName(self, "Select Non-Grid Image", "", "PNG/JPG Files (*.jpg *.png)")
        # fname[0] is the filepath
        if fname[0]:
            self.img = fname[0]
            self.t_radiostate[0] = True
            #attempt to load the other image paths
            if os.path.exists(fname[0][:-4]+"_grid"+fname[0][-4:]):
                self.gridimg = fname[0][:-4]+"_grid"+fname[0][-4:]
                self.t_radiostate[1] = True
            else:
                fname = qtw.QFileDialog.getOpenFileName(self, "Select Grid Image", "", "PNG/JPG Files (*.jpg *.png)")
                if fname[0]:
                    self.gridimg = fname[0]
                    self.t_radiostate[0] = True
                else:
                    self.gridimg = ""
                    self.t_radiostate[1] = False
            if os.path.exists(fname[0][:-4]+"_seg"+fname[0][-4:]):
                self.segimg = fname[0][:-4]+"_seg"+fname[0][-4:]
                self.segImageRadio.setEnabled(True)
            else:
                fname = qtw.QFileDialog.getOpenFileName(self, "Select Segmented Image", "", "PNG/JPG Files (*.jpg *.png)")
                if fname[0]:
                    self.segimg = fname[0]
                    self.t_radiostate[2] = True
                else:
                    self.t_radiostate[2] = False
                    self.segimg = ""
        else:
            self.img = ""
            self.t_radiostate[0] = False
        self.show_image(self.img)
        self.unlock_ui()
        print("Loaded images.")

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
        x2 = 1024 if x < 1024 else x
        y2 = 512 if y < 512 else y

        self.imageDisplay.setScene(self.scene)
        self.imageDisplay.setSceneRect(0, 0, x2, y2)
        self.scene.addPixmap(self.sample)

        # displaying the size of the image
        self.imageText.setText(f"Loaded {img.split('/')[-1]}: {x} by {y} pixels")
        print("Displayed image")

    def load_model(self):
        self.lock_ui()
        if os.path.exists(os.path.join(os.getcwd(),"model/pspnet_r50-d8_512x1024_40k_cityscapes.py")):
            self.cfg = "model/pspnet_r50-d8_512x1024_40k_cityscapes.py"
        else:
            fname = qtw.QFileDialog.getOpenFileName(self, "Select Config File", "", "Python File (*.py)")
            if fname[0]:
                self.cfg = fname[0]
            else:
                self.cfg = ""
            return
        if os.path.exists(os.path.join(os.getcwd(),"model/pspnet_r50-d8_512x1024_40k_cityscapes_.pth")):
            self.pth = "model/pspnet_r50-d8_512x1024_40k_cityscapes_.pth"
        else:
            fname = qtw.QFileDialog.getOpenFileName(self, "Select Weights", "", "PTH File (*.pth)")
            if fname[0]:
                self.pth = fname[0]
            else:
                self.mdl = ""
                self.pth = ""
                self.unlock_ui()
                return
        self.imageText.setText("Loading model...")
        print("Loading model...")
        from mmseg.apis import inference_segmentor, init_segmentor
        import mmcv
        print(self.cfg)
        print(self.pth)
        self.mdl = init_segmentor(self.cfg, self.pth, device='cuda:0')
        self.unlock_ui()
        print("Loaded model.")


    def segment_image(self):
        self.lock_ui()
        from mmseg.apis import inference_segmentor, init_segmentor
        import mmcv
        out_path = self.img[:-4]+"_seg"+self.img[-4:]
        clear_path=self.img[:-4]+"_seg2"+self.img[-4:]
        self.imageText.setText("")
        if self.img == "":
            self.imageText.setText("Please load an image first.\n")
        if self.mdl == "":
            self.imageText.setText(self.imageText.text()+"Please load a model first.")
        else:
            result = inference_segmentor(self.mdl,self.img)
            self.mdl.show_result(self.img,result, out_file=out_path,opacity=1.0)
            self.mdl.show_result(self.img,result, out_file=clear_path,opacity=0.5)
            self.segimg = out_path
            self.t_radiostate[2] = True
        self.unlock_ui()
        print("Segmented image generated.")

    def get_points(self):
        self.lock_ui()
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
            self.unlock_ui()
            return
        if len(self.gridimg) == 0:
            self.imageText.setText("No grid image found.")
            self.unlock_ui()
            return
        cv_img = cv2.imread(self.img)
        cv_gridimg = cv2.imread(self.gridimg)
        if cv_gridimg.shape != cv_img.shape:
            self.imageText.setText("Image sizes do not match.")
            self.unlock_ui()
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
        self.unlock_ui()
        self.imageText.setText(f"Points written to\n{savePath}")
        print("Points written.")

app = qtw.QApplication(sys.argv)
window = UI()
app.exec_()