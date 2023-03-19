import PyQt5.QtWidgets as qtw
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QImage, QColor
import sys, os, cv2, time
from PIL import Image
import numpy as np
from grid import Grid

import mmcv
from mmseg.apis import init_segmentor, inference_segmentor, train_segmentor
from mmseg.apis import show_result_pyplot as show_seg_result_pyplot
from mmcls.apis import init_model, inference_model, train_model
from mmcls.apis import show_result_pyplot as show_cls_result_pyplot

class UI(qtw.QMainWindow):
    # the paths of the images to be used for point counting
    img, gridimg, segimg = "", "", ""
    image = None
    # paths for model config, model, and weights
    seg_cfg, seg_pth, seg_mdl = "", "", ""
    cls_cfg, cls_pth, cls_mdl = "", "", ""
    t_buttonstate = [True,True,True,True,True,True,True,True,True,True,True]
    t_radiostate = [False,False,False]
    seg_cfg_path = "data/seg_test.py"
    seg_pth_path = "data/seg_test.pth"
    cls_cfg_path = "data/cls_test.py"
    cls_pth_path = "data/cls_test.pth"
    border_color = (255,136,255) #border color in RGB
    grid_color = (20,231,204) #grid color in RGB
    color_select = 0
    grid_mode = 0 #grid image for 0, image overlay for 1
    clear_mode = 0 #grid image for 0, grid overlay for 1
    def __init__(self):
        super(UI, self).__init__()
        self.init_paths()
        # prog.ui contains the layout of the app resulting from Qt Designer
        ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "sopia_ui.ui"))
        uic.loadUi(ui_path, self)

        #notification popup
        self.notif = qtw.QMessageBox()

        # "Assign functions to buttons"
        self.loadImage.clicked.connect(self.load_image)
        self.loadSeg.clicked.connect(self.load_seg_model)
        self.loadCls.clicked.connect(self.load_cls_model)
        self.segmentImage.clicked.connect(self.segment_image)
        self.classifyImage.clicked.connect(self.classify_image)
        self.getPoints.clicked.connect(self.get_points)
        self.changeMode.stateChanged.connect(self.change_mode)
        self.changeClear.stateChanged.connect(self.change_clear)

        #connect to grid detection functions
        self.selectBorder.clicked.connect(self.select_border)
        self.selectGrid.clicked.connect(self.select_grid)


        #connect to grid overlay functions
        self.createGrid.clicked.connect(self.create_grid)
        self.confirmGrid.clicked.connect(self.confirm_grid)
        self.hPositionLabel.hide()
        self.hPositionSlider.hide()
        self.hPositionSlider.valueChanged.connect(self.move_grid_h)
        self.vPositionLabel.hide()
        self.vPositionSlider.hide()
        self.vPositionSlider.valueChanged.connect(self.move_grid_v)

        # Connect radio buttons to load images
        self.normImageRadio.clicked.connect(self.radio_image)
        self.gridImageRadio.clicked.connect(self.radio_image)
        self.segImageRadio.clicked.connect(self.radio_image)

        self.imageDisplay.mousePressEvent = (self.get_color)
        self.scene = qtw.QGraphicsScene()
        self.imageDisplay.setScene(self.scene)
        self.show_color()

        self.show()

    def init_paths(self):
        if not os.path.exists(os.path.join(os.getcwd(),"data")):
            os.mkdir(os.path.join(os.getcwd(),"data"))
        if not os.path.exists(os.path.join(os.getcwd(),"save")):
            os.mkdir(os.path.join(os.getcwd(),"save"))

    def lock_ui(self):
        self.t_buttonstate = [self.loadImage.isEnabled(),self.loadSeg.isEnabled(),self.loadCls.isEnabled(),self.segmentImage.isEnabled(),self.getPoints.isEnabled(),self.selectBorder.isEnabled(),self.selectGrid.isEnabled(),self.confirmGrid.isEnabled(),self.createGrid.isEnabled(),self.changeMode.isEnabled(),self.changeClear.isEnabled()]
        self.t_radiostate = [self.normImageRadio.isEnabled(),self.gridImageRadio.isEnabled(),self.segImageRadio.isEnabled()]
        self.loadImage.setEnabled(False)
        self.loadSeg.setEnabled(False)
        self.loadCls.setEnabled(False)
        self.segmentImage.setEnabled(False)
        self.getPoints.setEnabled(False)
        self.selectBorder.setEnabled(False)
        self.selectGrid.setEnabled(False)
        self.confirmGrid.setEnabled(False)
        self.createGrid.setEnabled(False)
        self.changeMode.setEnabled(False)
        self.changeClear.setEnabled(False)
        self.normImageRadio.setEnabled(False)
        self.gridImageRadio.setEnabled(False)
        self.segImageRadio.setEnabled(False)
        time.sleep(0.1)

    def unlock_ui(self):
        self.loadImage.setEnabled(self.t_buttonstate[0])
        self.loadSeg.setEnabled(self.t_buttonstate[1])
        self.loadCls.setEnabled(self.t_buttonstate[2])
        self.segmentImage.setEnabled(self.t_buttonstate[3])
        self.getPoints.setEnabled(self.t_buttonstate[4])
        self.selectBorder.setEnabled(self.t_buttonstate[5])
        self.selectGrid.setEnabled(self.t_buttonstate[6])
        self.confirmGrid.setEnabled(self.t_buttonstate[7])
        self.createGrid.setEnabled(self.t_buttonstate[8])
        self.changeMode.setEnabled(self.t_buttonstate[9])
        self.changeClear.setEnabled(self.t_buttonstate[10])
        self.normImageRadio.setEnabled(self.t_radiostate[0])
        self.gridImageRadio.setEnabled(self.t_radiostate[1])
        self.segImageRadio.setEnabled(self.t_radiostate[2])
        time.sleep(0.1)

    def radio_image(self):
        if self.sender().text() == "Normal Image":
            self.show_image(self.img)
        elif self.sender().text() == "Grid Image":
            self.show_image(self.gridimg)
        elif self.sender().text() == "Segmented Image":
            self.show_image(self.segimg)
        else:
            self.imageText.setText(f"Unable to display image.")
        return

    def show_image(self,img):
        self.imageText.clear()
        self.imageText.setAutoFillBackground(False)
        self.scene.clear()
        #check if path to image exists
        if len(img) == 0:
            self.imageText.setText("Unable to load image.\nPlease reload all images.")
            return

        self.image = QImage(img)
        self.sample = QPixmap(QPixmap.fromImage(self.image))
        self.imageDisplay.setSceneRect(0, 0, self.sample.width(),self.sample.height())
        self.scene.addPixmap(self.sample)

        self.imageText.setText(f"Loaded {img.split('/')[-1]}: {self.sample.width()} by {self.sample.height()} pixels")
        print("Displayed image")
        return

    def load_image(self):
        self.lock_ui()
        # currently only accepting PNG files, but can be changed in the future just in case
        fname = qtw.QFileDialog.getOpenFileName(self, "Select Non-Grid Image", "data", "PNG/JPG Files (*.jpg *.png)")
        # fname[0] is the filepath
        if fname[0]:
            self.img = fname[0]
            self.t_radiostate[0] = True
            #attempt to load the other image paths
            if os.path.exists(fname[0][:-4]+"_grid"+fname[0][-4:]):
                self.gridimg = fname[0][:-4]+"_grid"+fname[0][-4:]
                self.t_radiostate[1] = True
            else:
                fname = qtw.QFileDialog.getOpenFileName(self, "Select Grid Image", "data", "PNG/JPG Files (*.jpg *.png)")
                if fname[0]:
                    self.gridimg = fname[0]
                    self.t_radiostate[1] = True
                else:
                    self.gridimg = ""
                    self.t_radiostate[1] = False
            if os.path.exists(fname[0][:-4]+"_seg"+fname[0][-4:]):
                self.segimg = fname[0][:-4]+"_seg"+fname[0][-4:]
                self.t_radiostate[2] = True
            else:
                fname = qtw.QFileDialog.getOpenFileName(self, "Select Segmented Image", "data", "PNG/JPG Files (*.jpg *.png)")
                if fname[0]:
                    self.segimg = fname[0]
                    self.t_radiostate[2] = True
                else:
                    self.segimg = ""
                    self.t_radiostate[2] = False
        else:
            self.img = ""
            self.t_radiostate[0] = False
        self.show_image(self.img)
        self.unlock_ui()
        print("Loaded images.")

    def load_seg_model(self):
        self.lock_ui()
        if os.path.exists(os.path.join(os.getcwd(),self.seg_cfg_path)):
            self.seg_cfg = self.seg_cfg_path
        else:
            fname = qtw.QFileDialog.getOpenFileName(self, "Select Config File", "mmsegmentation/configs/", "Python File (*.py)")
            if fname[0]:
                self.seg_cfg = fname[0]
            else:
                self.seg_cfg = ""
                self.unlock_ui()
                return
        if os.path.exists(os.path.join(os.getcwd(),self.seg_pth_path)):
            self.seg_pth = self.seg_pth_path
        else:
            fname = qtw.QFileDialog.getOpenFileName(self, "Select Weights", "mmsegmentation/work_dirs/sopia/", "PTH File (*.pth)")
            if fname[0]:
                self.seg_pth = fname[0]
            else:
                self.seg_cfg = ""
                self.seg_pth = ""
                self.unlock_ui()
                return
        self.imageText.setText("Loading model...")
        print("Loading model...")
        try:
            self.seg_mdl = init_segmentor(self.seg_cfg, self.seg_pth, device='cuda:0')
            self.imageText.setText("Loaded model.")
            print("Loaded model to gpu.")
        except AssertionError as e:
            if e:
                try:
                    self.seg_mdl = init_segmentor(self.seg_cfg, self.seg_pth, device='cpu')
                    self.imageText.setText("Loaded model.")
                    print("Loaded model to cpu.")
                except:
                    self.imageText.setText("Unable to load model.")
                    print("Unable to load model.")
        except Exception as e:
            self.imageText.setText("Unable to load model.")
            print("Unable to load model.")
            self.seg_mdl = ""
        finally:
            self.unlock_ui()

    def load_cls_model(self):
        self.lock_ui()
        if os.path.exists(os.path.join(os.getcwd(),self.cls_cfg_path)):
            self.cls_cfg = self.cls_cfg_path
        else:
            fname = qtw.QFileDialog.getOpenFileName(self, "Select Config File", "mmclassification/configs/", "Python File (*.py)")
            if fname[0]:
                self.cls_cfg = fname[0]
            else:
                self.cls_cfg = ""
                self.unlock_ui()
                return
        if os.path.exists(os.path.join(os.getcwd(),self.cls_pth_path)):
            self.cls_pth = self.cls_pth_path
        else:
            fname = qtw.QFileDialog.getOpenFileName(self, "Select Weights", "mmclassification/work_dirs/sopia/", "PTH File (*.pth)")
            if fname[0]:
                self.cls_pth = fname[0]
            else:
                self.cls_cfg = ""
                self.cls_pth = ""
                self.unlock_ui()
                return
        self.imageText.setText("Loading model...")
        print("Loading model...")
        try:
            self.cls_mdl = init_model(self.cls_cfg, self.cls_pth, device='cuda:0')
            self.imageText.setText("Loaded model.")
            print("Loaded model to gpu.")
        except AssertionError as e:
            if e:
                try:
                    self.cls_mdl = init_model(self.cls_cfg, self.cls_pth, device='cpu')
                    self.imageText.setText("Loaded model.")
                    print("Loaded model to cpu.")
                except:
                    self.imageText.setText("Unable to load model.")
                    print("Unable to load model.")
        except Exception as e:
            self.imageText.setText("Unable to load model.")
            print("Unable to load model.")
            self.cls_mdl = ""
        finally:
            self.unlock_ui()

    def segment_image(self):
        self.lock_ui()
        if self.img == "":
            self.imageText.setText("Please load an image first.")
        elif self.seg_mdl in ["",None]:
            self.imageText.setText("Please load a model first.")
        else:
            self.imageText.setText("Segmenting image...")
            print("Segmenting image...")
            try:
                out_path = self.img[:-4]+"_seg"+self.img[-4:]
                result = inference_segmentor(self.seg_mdl,self.img)
                show_seg_result_pyplot(self.seg_mdl, self.img, result, out_file=out_path)
                self.segimg = out_path
                print("Segmentation complete.")
                self.t_radiostate[2] = True
                self.imageText.setText("Segmented image generated.")
            except:
                self.imageText.setText("Unable to segment image.")
        self.unlock_ui()
        return

    def classify_image(self):
        self.lock_ui()
        if self.img == "":
            self.imageText.setText("Please load an image first.")
        elif self.cls_mdl in ["",None]:
            self.imageText.setText("Please load a model first.")
        else:
            self.imageText.setText("Classifying image...")
            print("Classifying image...")
            try:
                out_path = self.img[:-4]+"_cls"+self.img[-4:]
                result = inference_model(self.cls_mdl,self.img)
                print("Classification complete.")
                self.imageText.setText(f"Result: {result['pred_class']}-{result['pred_label']}({result['pred_score']})")
                self.t_radiostate[2] = True
            except:
                self.imageText.setText("Unable to classify image.")
        self.unlock_ui()
        return
    
    def classify_point(self,img):
        print("Classifying...")
        print(img)
        if not(img == "" or self.cls_mdl in ["",None]):
            print("Classed as:")
            try:
                result = inference_model(self.cls_mdl,img)
                print(f"Result: {result['pred_class']}-{result['pred_label']}({result['pred_score']})")
                return f"{result['pred_class']}-{result['pred_label']}({result['pred_score']})"
            except:
                pass
        return 
    
    def change_mode(self):
        self.lock_ui()
        self.grid_mode = self.changeMode.isChecked()
        if self.changeMode.isChecked():
            print("Switching to grid image mode.")
            self.t_radiostate[1] = True
        else:
            print("Switching to grid overlay mode.")
            self.t_radiostate[1] = False
        self.grid_img = ""
        self.t_radiostate[1] = False
        self.unlock_ui()

    def change_clear(self):
        self.lock_ui()
        self.clear_mode = self.changeClear.isChecked()
        if self.changeClear.isChecked():
            print("Switching to clear grid overlay.")
        else:
            print("Switching to legacy mode.")
        self.grid_img = ""
        self.unlock_ui()

    def select_border(self):
        if self.grid_mode == 0:
            self.lock_ui()
            self.color_select = 1

    def select_grid(self):
        if self.grid_mode == 0:
            self.lock_ui()
            self.color_select = 2

    def get_color(self,event):
        x = event.pos().x()
        y = event.pos().y()
        if self.image is not None:
            pixcol = QColor(self.image.pixel(x+self.imageDisplay.horizontalScrollBar().value(),y+self.imageDisplay.verticalScrollBar().value())).getRgb()[:3]
            print(f"Position: ({x+self.imageDisplay.horizontalScrollBar().value()},{y+self.imageDisplay.verticalScrollBar().value()})")
            print(f"Pixel Color: {pixcol}")
            if self.color_select == 0:
                return
            elif self.color_select == 1:
                self.border_color = pixcol
                self.unlock_ui()
            elif self.color_select == 2:
                self.grid_color = pixcol
                self.unlock_ui()
            self.show_color()
            self.color_select = 0

    def show_color(self):
        self.borderColorLabel.setStyleSheet("background-color: rgb{};".format(self.border_color))
        self.gridColorLabel.setStyleSheet("background-color: rgb{};".format(self.grid_color))

    def create_grid(self):
        if self.grid_mode == 0:
            return
        if self.segImageRadio.isChecked():
            self.gridLabel = qtw.QLabel()
            self.gridLabel.setStyleSheet("QLabel {background-color: rgba(0,0,0,0);}")
            self.ui = Grid(self)
            self.ui.show()
        else:
            self.notif.setIcon(qtw.QMessageBox.Critical)
            self.notif.setText("Please select the segmented image first.")
            self.notif.setWindowTitle("Error")
            self.notif.exec()
        return
    
    def move_grid_h(self, value):
        y = self.gridLabel.y()
        self.gridLabel.move(value, y)
        return

    def move_grid_v(self, value):
        x = self.gridLabel.x()
        self.gridLabel.move(x, value)
        return

    def confirm_grid(self):
        if self.grid_mode == 0:
            return
        self.lock_ui()
        if self.img:
            out_path = self.segimg[:-4]+"_with_grid"+self.segimg[-4:]
            img1 = Image.open(self.segimg)
            img2 = Image.open("overlay.png")
            temp_im = img1.copy()
            temp_im.paste(img2, (self.gridLabel.x(), self.gridLabel.y()), img2)  # use img2.convert('RGBA') in case "bad transparency mask" error comes up
            temp_im.save(out_path, "PNG")
            self.gridimg = out_path
            self.t_radiostate[1] = True
            self.grid_color = (0, 255, 255)
            self.hPositionSlider.setEnabled(False)
            self.vPositionSlider.setEnabled(False)
        self.unlock_ui()
        return

    def get_points(self):
        pt_rad = 25
        self.lock_ui()
        #set boundaries for grid color in HSV format
        border_hsv = cv2.cvtColor(np.uint8([[self.border_color]]),cv2.COLOR_RGB2HSV)[0][0]
        grid_hsv = cv2.cvtColor(np.uint8([[self.grid_color]]),cv2.COLOR_RGB2HSV)[0][0]
        border_colorl=np.clip([i-5 for i in border_hsv],a_min=0,a_max=[179,255,255])
        border_coloru=np.clip([i+5 for i in border_hsv],a_min=0,a_max=[179,255,255])
        grid_colorl=np.clip([i-15 for i in grid_hsv],a_min=0,a_max=[179,255,255])
        grid_coloru=np.clip([i+15 for i in grid_hsv],a_min=0,a_max=[179,255,255])

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
        cv_img = cv2.imread(self.img if self.grid_mode == 0 else self.segimg)
        cv_gridimg = cv2.imread(self.gridimg)
        if cv_gridimg.shape != cv_img.shape:
            self.imageText.setText("Image sizes do not match.")
            self.unlock_ui()
            return

        #filter grid and borders before getting lines
        img_l,img_w = cv_img.shape[0],cv_img.shape[1]
        hsv_img = cv2.cvtColor(cv_gridimg,cv2.COLOR_BGR2HSV)
        cv2.imwrite(os.path.join(savePath,"hsv.png"),hsv_img)

        gridmask_img = cv2.inRange(hsv_img,grid_colorl,grid_coloru)
        gridim_cv = cv2.bitwise_and(hsv_img,hsv_img,mask=gridmask_img)
        gridim_g = cv2.cvtColor(gridim_cv,cv2.COLOR_RGB2GRAY)
        gridedges = cv2.Canny(gridim_g, 50, 200, None, apertureSize=3)
        cv2.imwrite(os.path.join(savePath,"gridmask.png"),gridmask_img)
        cv2.imwrite(os.path.join(savePath,"Grid Filter.png"),gridim_cv)
        cv2.imwrite(os.path.join(savePath,"edge.png"),gridedges)


        if self.grid_mode == 0:
            bordermask_img = cv2.inRange(hsv_img,border_colorl,border_coloru)
            borderim_cv = cv2.bitwise_and(hsv_img,hsv_img,mask=bordermask_img)
            borderim_g = cv2.cvtColor(borderim_cv,cv2.COLOR_RGB2GRAY)
            borderedges = cv2.Canny(borderim_g, 50, 200, None, apertureSize=3)
            cv2.imwrite(os.path.join(savePath,"bordermask.png"),bordermask_img)
            cv2.imwrite(os.path.join(savePath,"Border Filter.png"),borderim_cv)
            cv2.imwrite(os.path.join(savePath,"border.png"),borderedges)
            #First hough transform: obtain locations of image borders
            lines = cv2.HoughLines(borderedges, 1, np.pi/180, 500)
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
            #for h in range(len(h_lines)):
                #for v in range(len(v_lines)):
                    #cv2.circle(borderim_cv, (h_lines[h],v_lines[v]),5,(255,0,0),thickness = 5)
                    #cv2.circle(cv_gridimg, (h_lines[h],v_lines[v]),25,(255,0,0),thickness = 2)
            cv2.imwrite(os.path.join(savePath,"output_border.png"),borderim_cv)
        else:
            xmin,xmax,ymin,ymax=0,img_l,0,img_w


        #Hough transform: obtain coordinates of grid intersections
        lines = cv2.HoughLines(gridedges, 1, np.pi/180, 500)
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
                #cv2.circle(gridim_cv, (h_lines[h],v_lines[v]),pt_rad,(255,0,0),thickness = 5)
                #cv2.circle(cv_gridimg, (h_lines[h],v_lines[v]),pt_rad,(0,255,0),thickness = 2)
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

        if self.grid_mode == 0:
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
                        coords += f"({h}, {v})  ({h_lines[h]}, {v_lines[v]})"
                        #cv2.circle(cv_segimg, (h_lines[h],v_lines[v]),pt_rad,(0,255,0),thickness = 2)
                        r1,r2,r3,r4 =(h_lines[h]-pt_rad),(h_lines[h]+pt_rad),(v_lines[v]-pt_rad),(v_lines[v]+pt_rad)
                        temp = cv2.cvtColor(cv_segimg[r3:r4,r1:r2], cv2.COLOR_BGR2BGRA)
                        temp[:,:,3] = blank_mask[:,:,0]
                        imagePath = os.path.join(raw_path,f"{os.path.split(self.img)[1].split('.')[0]}_({h},{v})_{h_lines[h]}_{v_lines[v]}_50.png")
                        print(imagePath)
                        cv2.imwrite(imagePath,temp)
                        coords += f" - {self.classify_point(imagePath)}\n"
                cv2.imwrite(os.path.join(savePath,"rawoutput.png"),cv_segimg)
                file = open(f"{savePath}/rawcoordinates.txt", "w+")
                file.write(coords)
                file.close()
                self.outputDisplay.append(coords)

        self.unlock_ui()
        self.imageText.setText(f"Points written to\n{savePath}")
        print("Points written.")
        return

app = qtw.QApplication(sys.argv)
window = UI()
app.exec_()