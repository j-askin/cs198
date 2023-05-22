import os, cv2, time
from PIL import Image
import numpy as np
import mmcv
from mmseg.apis import init_model, inference_model, show_result_pyplot
class Points:
    def __init__(self,h_lines = [],v_lines = [],image = [],mask = [],classes = [],palette = []):
        self.h_lines = h_lines
        self.v_lines = v_lines
        print(h_lines)
        print(v_lines)
        self.image = image
        self.mask = mask
        self.classes = classes
        self.palette = palette
        self.points = np.zeros((len(self.v_lines),len(self.h_lines),3),np.uint8) #stores the point colors
        self.point_class = [["" for i in range(len(self.h_lines))] for j in range(len(self.v_lines))] #stores the point classes
        print(self.point_class)
        print(self.points[:,:,0])
        for v in range(len(self.v_lines)):
            for h in range(len(self.h_lines)):
                self.points[v,h] = self.mask[self.v_lines[v],self.h_lines[h]][::-1]
                self.point_class[v][h] = self.classify_point(v,h)

    def save_points(self,dir_path=os.path.dirname(__file__),save_path="save",log=False,pt_rad=0):
        logfile = ""
        if True:#try:
            save_path = os.path.join(save_path,f"{time.strftime('%m%y%d-%H%M%S',time.localtime(time.time()))}")
            if (log or pt_rad>0):
                if not verify_path(dir_path,save_path):
                    logfile="Error: unable to save results to file\n"
                    raise Exception
            if pt_rad > 0:
                pt_path = os.path.join(save_path,"sample_points")
                pt_mask_path = os.path.join(save_path,"mask_points")
                if not(verify_path(dir_path,pt_path) and verify_path(dir_path,pt_mask_path)):
                    logfile="Error: unable to save results to file\n"
                    raise Exception
                print(self.image.shape)
                image_overlay = np.zeros(self.image.shape, np.uint8)
                image_overlay = cv2.cvtColor(image_overlay, cv2.COLOR_BGR2BGRA)
                image_overlay[:,:] = [127,127,127,255]
                print(image_overlay)
                mask_overlay = np.zeros(self.mask.shape, np.uint8)
                mask_overlay = cv2.cvtColor(image_overlay, cv2.COLOR_BGR2BGRA)
                mask_overlay[:,:] = [127,127,127,255]
                print(mask_overlay)
            class_count = []
            logfile += "Sample Coordinates:\n"
            for v in range(len(self.v_lines)):
                for h in range(len(self.h_lines)):
                    logfile += f"Point ({h}, {v}) ({self.h_lines[h]}, {self.v_lines[v]})\n"
                    logfile += f"{self.points[v,h]} => {self.point_class[v][h]}\n"
                    class_count.append(self.point_class[v][h])
                    if pt_rad > 0:
                        r1,r2,r3,r4 =max(self.h_lines[h]-pt_rad,0),min(self.h_lines[h]+pt_rad,image_overlay.shape[1]-1),max(self.v_lines[v]-pt_rad,0),min(self.v_lines[v]+pt_rad,image_overlay.shape[0]-1)
                        image_overlay[r3:r4,r1:r2,:3] = self.image[r3:r4,r1:r2]
                        mask_overlay[r3:r4,r1:r2,:3] = self.points[v,h]
            if pt_rad > 0:
                mask_overlay = cv2.cvtColor(mask_overlay, cv2.COLOR_RGBA2BGRA)
                cv2.imwrite(os.path.join(dir_path,save_path,"image_overlay.png"),image_overlay)
                cv2.imwrite(os.path.join(dir_path,save_path,"mask_overlay.png"),mask_overlay)
                cv2.imwrite(os.path.join(dir_path,save_path,"image.png"),self.image)
                cv2.imwrite(os.path.join(dir_path,save_path,"mask.png"),self.mask)
            class_types = list(set(class_count))
            class_types.sort()
            for class_type in class_types:
                logfile += f"{class_type}: {round(class_count.count(class_type)*100/len(class_count),3)}%\n"
            if log:
                with open(f"{os.path.join(dir_path,save_path)}/coordinates.txt", "w+") as f:
                    f.write(logfile)
        #except:
            #logfile = "Unable to get points.\n"
        path = os.path.join(dir_path,save_path)
        return logfile, path

    def classify_point(self,y,x):
        try:
            for i in range(len(self.classes)):
                if tuple(self.points[y,x,:3]) == tuple(self.palette[i]):
                    return self.classes[i]
            return "UNKNOWN MATERIAL"
        except:
            return "NO MATCH"
    
    def update_point(self,y,x,new_class):
        msg = ""
        try:
            if (y >= len(self.classes) or y < 0 or x >= len(self.classes) or x < 0):
                msg += "Point is out of bounds."
                return msg
            for i in range(len(self.classes)):
                if new_class == self.classes[i]:
                    msg += (f"Changed point ({x},{y}) class from {self.point_class[y][x]} to {self.classes[i]}")
                    self.point_class[y][x] = self.classes[i]
                    return msg
            msg += (f"Changed point ({x},{y}) class from {self.point_class[y][x]} to UNKNOWN MATERIAL")
            self.point_class[y][x] = "UNKNOWN MATERIAL"
            return msg
        except:
            msg += (f"Changed point ({x},{y}) class from {self.point_class[y][x]} to NO MATCH")
            self.point_class[y][x] = "NO MATCH"
            return msg

def verify_path(dir_path=os.path.dirname(__file__),file_path=""):
    #prevent any access to directories outside the project folder
    abs_path = os.path.abspath(os.path.join(dir_path, file_path))
    print(abs_path)
    if not abs_path.lower().startswith(os.path.join(os.pardir,os.path.dirname(__file__)).lower()):
        print("Invalid directory.")
        return False
    try:
        os.makedirs(os.path.dirname(abs_path),exist_ok=True)
        print("Directory exists.")
        return True
    except:
        print("Invalid directory.")
        return False

def verify_file(dir_path=os.path.dirname(__file__),file_path=""):
    if verify_path(dir_path,os.path.split(file_path)[0]):
        print(os.path.join(dir_path, file_path))
        if os.path.isfile(os.path.abspath(os.path.join(dir_path, file_path))):
            return True
    return False

#All paths returned are relative paths to the program file at the root of the project directory.

def load_image(dir_path=os.path.join(os.path.dirname(__file__),"images"),image_path="",image_type="sample"):
    msg = ""
    image = ""
    try:
        if not verify_file(dir_path,image_path):
            raise Exception
        image = os.path.join(dir_path,image_path)
        msg += f"Loaded {image_type} image {image}\n"
    except:
        image = ""
        msg = f"Unable to load {image_type} image.\n"
    finally:
        return image, msg

def load_model_from_name(dir_path = "",model_path = ""):
    msg = ""
    try:
        config_path = model_path+".py"
        pth_path = model_path+".pth"
    except:
        config_path,pth_path = "",""
    finally:
        return load_model(dir_path,config_path,pth_path)

def load_model(dir_path=os.path.join(os.path.dirname(__file__),"models"),config_path = "",pth_path = ""):
    msg = ""
    cfg, pth, model = "", "", ""
    try:
        msg += f"Attempting to load segmenter config {os.path.join(dir_path,config_path)}\n"
        if not verify_file(dir_path,config_path):
            msg += "Unable to load segmenter config.\n"
            raise Exception
        cfg = os.path.join(dir_path,config_path)
        msg += f"Attempting to load segmenter path {os.path.join(dir_path,pth_path)}\n"
        if not verify_file(dir_path,pth_path):
            msg += "Unable to load segmenter path.\n"
            raise Exception
        pth = os.path.join(dir_path,pth_path)
        msg += "Loading segmentation model...\n"
        try:
            model = init_model(cfg, pth, device='cuda:0')
            msg += "Loaded segmentation model to gpu.\n"
        except AssertionError as e:
                model = init_model(cfg, pth, device='cpu')
                msg += "Loaded segmentation model to cpu.\n"
    except Exception as e:
        msg += f"Unable to load model: {e}\n"
    finally:
        return model

def segment_image(dir_path=os.path.join(os.path.dirname(__file__),"images"), mask_path="mask.mask.png",image = "", model = None, show=False):
    msg = ""
    mask_image = ""
    out_path = ""
    try:
        if not verify_file(dir_path,image):
            msg += "Please load an image first.\n"
            raise Exception
        elif model == None:
            msg += "Please load a model first.\n"
            raise Exception
        else:
            msg += f"Segmenting image {image}...\n"
            img_name = os.path.join(dir_path, image)
            result = inference_model(model, img_name)
            mask_image = grid_image=os.path.join(dir_path, mask_path)
            show_result_pyplot(model=model, img=img_name, result=result, opacity=1.0, show=show,out_file=mask_image)
            if not verify_file(dir_path,mask_image):
                msg += "Unable to load segmenter config.\n"
                raise Exception
    except Exception as e:
        mask_image = ""
        msg += f"Unable to generate segmented mask image: {e}\n"
    finally:
        msg += f"Segmented mask image generated to {mask_image}.\n"

    return mask_image,msg

def str2int(string,default = 0):
    try:
        return int(string)
    except:
        return default

def create_grid(dir_path=os.path.join(os.path.dirname(__file__),"images"), grid_path = "grid.grid.png",
                row_count = 5, col_count = 5, row_space = 320, col_space = 200,
                grid_w = 1920, grid_l = 1200, grid_x = 320, grid_y = 200):
    msg=""
    grid_image = ""
    print(os.path.split(os.path.join(dir_path,grid_path))[0])
    os.makedirs(os.path.split(os.path.join(dir_path,grid_path))[0],exist_ok=True)
    if not grid_path.lower().endswith(".png"):
        grid_path = grid_path+".png"
    row_count = str2int(row_count,5)
    row_space = str2int(row_space,320)
    col_count = str2int(col_count,5)
    col_space = str2int(col_space,200)
    grid_w = str2int(string=grid_w, default=1920)
    grid_x = str2int(grid_x,320)
    grid_l = str2int(string=grid_l, default=1200)
    grid_y = str2int(string=grid_y, default=200)
    grid_height = row_count + (row_count * row_space) - row_space
    grid_width = col_count + (col_count * col_space) - col_space
    grid = np.zeros((grid_l,grid_w,4))
    for j in range(grid_l):
        for i in range(grid_w):
            if j >= grid_y and j < grid_y+grid_height and i >= grid_x and i < grid_x+grid_width:
                if (j-grid_y)%(col_space+1) == 0 and (i-grid_x)%(row_space+1) == 0:
                    grid[j,i]=(0,255,255,255)
                elif (j-grid_y)%(col_space+1) == 0:
                    grid[j,i]=((255,0,255,255) if j%2 == 0 else (128,0,128,255))
                elif (i-grid_x)%(row_space+1) == 0:
                    grid[j,i]=((255,255,0,255) if i%2 == 0 else (128,128,0,255))
                else:
                    grid[j,i]=(0,0,0,0)
    grid=Image.fromarray(grid.astype("uint8"),"RGBA")
    grid_image=os.path.join(dir_path, grid_path)
    grid.save(grid_image, "PNG")
    msg += f"Saved grid to {grid_path}\n"
    return grid_image,msg

def get_points(dir_path=os.path.join(os.path.dirname(__file__),"images"),image_path="",grid_path="",mask_path="",model="",save_path="save",timestamp=True):
    msg = ""
    if True:#try:
        #verify images
        if verify_file(dir_path,image_path):
            cv_image = cv2.imread(os.path.join(dir_path,image_path))
        else:
            msg += "No image found.\n"
            raise Exception
        if verify_file(dir_path,grid_path):
            cv_grid_image = cv2.imread(os.path.join(dir_path,grid_path))
        else:
            msg += "No grid image found.\n"
            raise Exception
        if verify_file(dir_path,mask_path):
            cv_mask_image = cv2.imread(os.path.join(dir_path,mask_path))
        else:
            msg += "No segmented mask image found.\n"
            raise Exception
        if model in ["",None]:
            msg += "No model loaded.\n"
            raise Exception

        image_l,image_w = cv_image.shape[0],cv_image.shape[1]
        cv_graygrid_image = cv2.cvtColor(cv_grid_image,cv2.COLOR_BGR2GRAY)
        cv2.imwrite(os.path.join(dir_path,"gridgray.png"),cv_graygrid_image)
        #Hough transform: obtain coordinates of grid intersections
        lines = cv2.HoughLines(cv_graygrid_image, 1, np.pi/180, 500)
        h_lines, v_lines = [],[]
        for line in lines:
            rho = line[0][0]
            theta = line[0][1]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = rho*np.cos(theta)
            y0 = rho*np.sin(theta)
            pt1 = (int(x0 + image_w*(-b)), int(y0 + image_l*(a)))
            pt2 = (int(x0 - image_w*(-b)), int(y0 - image_l*(a)))
            if theta == 0:
                h_lines.append(pt1[0])
            else:
                v_lines.append(pt2[1])
            cv2.line(cv_graygrid_image, pt1, pt2, (255,255,255), 3, cv2.LINE_AA)
        h_lines.sort()
        v_lines.sort()

        #verify that all points are within the image.
        if h_lines[-1] >= image_w and v_lines[-1] >= image_l:
            msg += "Grid image does not fit inside sample image.\n"
            #raise Exception

        #generate points object
        grid_points = Points(h_lines,v_lines,cv_image,cv_mask_image,model.dataset_meta["classes"],model.dataset_meta["palette"])
        msg += "Points obtained."

    #except Exception as e:
        #msg += "Unable to get points.\n"
        #grid_points = Points()
    return grid_points,msg