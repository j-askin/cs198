import concretile
import os, cv2, time
from PIL import Image
import numpy as np
import mmcv
from mmseg.apis import init_model, inference_model, show_result_pyplot
def get_points(dir_path=os.path.join(os.path.dirname(__file__),"images"),image_path="",grid_path="",mask_path="",model="",save_path="save",timestamp=True):
    msg = ""
    print("1")
    if True:#try:
        #verify images
        if concretile.verify_file(dir_path,image_path):
            cv_image = cv2.imread(os.path.join(dir_path,image_path))
        else:
            msg += "No image found.\n"
            raise Exception
        if concretile.verify_file(dir_path,grid_path):
            cv_grid_image = cv2.imread(os.path.join(dir_path,grid_path))
        else:
            msg += "No grid image found.\n"
            raise Exception
        if concretile.verify_file(dir_path,mask_path):
            cv_mask_image = cv2.imread(os.path.join(dir_path,mask_path))
        else:
            msg += "No segmented mask image found.\n"
            raise Exception
        if model in ["",None]:
            msg += "No model loaded.\n"
            raise Exception
        print("2")

        image_l,image_w = cv_image.shape[0],cv_image.shape[1]
        cv_graygrid_image = cv2.cvtColor(cv_grid_image,cv2.COLOR_BGR2GRAY)
        cv2.imwrite(os.path.join(dir_path,"gridgray.png"),cv_graygrid_image)
        #Hough transform: obtain coordinates of grid intersections
        lines = cv2.HoughLines(cv_graygrid_image, 1, np.pi/180, 500)
        print("3")
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
        print("4")

        #verify that all points are within the image.
        if h_lines[-1] >= image_w and v_lines[-1] >= image_l:
            msg += "Grid image does not fit inside sample image.\n"
            #raise Exception

        print("5")
        #generate points object
        grid_points = concretile.Points(h_lines,v_lines,cv_image,cv_mask_image,model.dataset_meta["classes"],model.dataset_meta["palette"])
        msg += "Points obtained."
        print("6")

    #except Exception as e:
        #msg += "Unable to get points.\n"
        #grid_points = Points()
    return grid_points,msg

root_dir = os.path.dirname(__file__)
static = os.path.join(root_dir,"static")
template = os.path.join(root_dir,"templates")
image_dir = os.path.join(static,"images")
model_dir = os.path.join(static,"models")
save_dir = os.path.join(static,"save")
img = os.path.join(static,"images/uploads/10.jpg")
mask_img = os.path.join(static,"images/uploads/mask/10.mask.png")
grid_img = os.path.join(static,"images/uploads/grid/grid_make.grid.png")
config = os.path.join(static,"models/lumenstone_upernet/lumenstone_upernet.py")
pth = os.path.join(static,"models/lumenstone_upernet/lumenstone_upernet.pth")
model = concretile.load_model(static,config,pth)
print("Begin")
concretile.get_points(static,img,grid_img,mask_img,model)