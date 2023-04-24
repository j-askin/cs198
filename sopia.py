import os, cv2, time
from PIL import Image
import numpy as np
import mmcv
from mmseg.apis import init_model, inference_model, show_result_pyplot

def verify_path(dir_path=os.path.dirname(__file__),file_path=""):
    #prevent any access to directories outside the project folder
    abs_path = os.path.abspath(os.path.join(dir_path, file_path))
    print(abs_path)
    print(os.path.join(os.pardir,os.path.dirname(__file__)))
    if not abs_path.lower().startswith(os.path.join(os.pardir,os.path.dirname(__file__)).lower()):
        print("Invalid directory.")
        return False
    if not os.path.exists(os.path.dirname(abs_path)):
        try:
            os.mkdir(os.path.dirname(abs_path))
            print("Directory added.")
        except:
            print("Invalid directory.")
            return False
    else:
        print("Directory exists.")
        return True

def verify_file(dir_path=os.path.dirname(__file__),file_path=""):
    if verify_path(dir_path,file_path):
        print(os.path.abspath(os.path.join(dir_path, file_path)))
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
        msg += f"Attempting to load segmenter config {os.path.join(os.path.dirname(__file__),config_path)}\n"
        if not verify_file(dir_path,config_path):
            msg += "Unable to load segmenter config.\n"
            raise Exception
        cfg = os.path.join(os.path.dirname(__file__),config_path)
        msg += f"Attempting to load segmenter path {os.path.join(os.path.dirname(__file__),pth_path)}\n"
        if not verify_file(dir_path,pth_path):
            msg += "Unable to load segmenter path.\n"
            raise Exception
        pth = os.path.join(os.path.dirname(__file__),pth_path)
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
        return cfg,pth,model,msg

def segment_image(dir_path=os.path.join(os.path.dirname(__file__),"images"),image = "", model = "",mask_path = "mask.png", show=False):
    msg = ""
    mask_image = ""
    out_path = ""
    try:
        if not verify_file(dir_path,image):
            msg += "Please load an image first.\n"
            raise Exception
        elif model in ["",None]:
            msg += "Please load a model first.\n"
            raise Exception
        else:
            msg += f"Segmenting image {image}...\n"
            result = inference_model(model,image)
            mask_image = (os.path.splitext(image))[0]+"_mask.png"
            out_path = os.path.abspath(os.path.join(dir_path, mask_image))
            show_result_pyplot(model, image, result, opacity=1, show=show,out_file=out_path)
            if not verify_file(dir_path,mask_image):
                msg += "Unable to load segmenter config.\n"
                raise Exception
    except Exception as e:
        mask_image = ""
        out_path = ""
        msg += f"Unable to generate segmented mask image: {e}\n"
    finally:
        msg += f"Segmented mask image generated to {out_path}.\n"

    return mask_image,msg

def str2int(string,default = 0):
    try:
        return int(string)
    except:
        return default

def create_grid(dir_path=os.path.join(os.path.dirname(__file__),"images"),  row_count = 5,col_count = 5,row_space = 320,col_space = 200,grid_w = 1920, grid_l = 1200, grid_x = 320, grid_y = 200,grid_path = "grid.png"):
    msg=""
    grid_image = ""
    try:
        if not grid_path.lower().endswith(".png"):
            grid_path = grid_path+".png"
        row_count = str2int(row_count,0)
        row_space = str2int(row_space,0)
        col_count = str2int(col_count,0)
        col_space = str2int(col_space,0)
        grid_w = str2int(grid_w,"")
        grid_x = str2int(grid_x,0)
        grid_l = str2int(grid_l,"")
        grid_y = str2int(grid_y,0)
        if "" in [grid_w,grid_l]:
            msg += "Error: unknown grid image size.\n"
            raise Exception
        else:
            grid_width = row_count + (row_count * row_space) - row_space
            grid_height = col_count + (col_count * col_space) - col_space
            grid = np.zeros((grid_l,grid_w,4))
            print(row_space+1)
            print(col_space+1)
            for i in range(grid_l):
                for j in range(grid_w):
                    if i >= grid_y and i < grid_y+grid_height and j >= grid_x and j < grid_x+grid_width:
                        if (i-grid_y)%(col_space+1) == 0 and (j-grid_x)%(row_space+1) == 0:
                            grid[i,j]=(0,255,255,255)
                        elif (i-grid_y)%(col_space+1) == 0:
                            grid[i,j]=((255,0,255,255) if j%2 == 0 else (128,0,128,255))
                        elif (j-grid_x)%(row_space+1) == 0:
                            grid[i,j]=((255,255,0,255) if i%2 == 0 else (128,128,0,255))
                        else:
                            grid[i,j]=(0,0,0,0)
            np.resize(grid,(grid_l,grid_w,4))
            grid=Image.fromarray(grid.astype("uint8"),"RGBA")
            grid_image=os.path.abspath(os.path.join(dir_path, grid_path))
            grid.save(grid_image, "PNG")
            if not verify_file(dir_path,grid_path):
                msg += "Error: could not save grid.\n"
                raise Exception
            msg += f"Saved grid to {grid_path}\n"
    except Exception as e:
        grid_image = ""
        msg += "Unable to generate grid: {e}\n"
    finally:
        return grid_image,msg

def classify_point(color = (0,0,0),model=None):
    try:
        materials = list(zip(model.CLASSES,model.PALETTE))
        for material in materials:
            if tuple(color) == tuple(material[1]):
                return material[0]
        return "UNKNOWN MATERIAL"
    except:
        return "NO MATCH"

def get_points(dir_path=os.path.join(os.path.dirname(__file__),"images"),image="",grid_image="",mask_image="",model="",pt_rad=25,save_path="save",timestamp=True):
    msg = ""
    coords = ""
    pt_mode = True
    try:
        if timestamp:
            save_path = os.path.join(save_path,f"{time.strftime('%m%y%d-%H%M%S',time.localtime(time.time()))}")
        pt_path = os.path.join(save_path,"sample_points")
        pt_mask_path = os.path.join(save_path,"mask_points")
        if not (verify_path(dir_path,save_path) and verify_path(dir_path,pt_path) and verify_path(dir_path,pt_mask_path)):
            msg+="Error: unable to save results\n"
            raise Exception
        pt_rad = str2int(pt_rad,1)
        #verify images
        if verify_file(dir_path,image):
            cv_image = cv2.imread(image)
        else:
            msg += "No image found.\n"
            raise Exception
        if verify_file(dir_path,grid_image):
            cv_grid_image = cv2.imread(grid_image)
        else:
            msg += "No grid image found.\n"
            raise Exception
        if verify_file(dir_path,mask_image):
            cv_mask_image = cv2.imread(mask_image)
        else:
            pt_mode = False
            msg += "No segmented mask image found. Proceeding without point identification.\n"
        if model in ["",None]:
            pt_mode = False
            msg += "No model loaded. Proceeding without point identification. \n"


        image_l,image_w = cv_image.shape[0],cv_image.shape[1]
        cv_graygrid_image = cv2.cvtColor(cv_grid_image,cv2.COLOR_BGR2GRAY)

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
            raise Exception

        #Output all coordinates
        class_count = []
        blank_mask = np.zeros((pt_rad*2,pt_rad*2,3), np.uint8)
        cv2.circle(blank_mask, (pt_rad,pt_rad),pt_rad,(255,255,255),thickness = -1)
        coords += "Sample Coordinates:\n"
        for h in range(len(h_lines)):
            for v in range(len(v_lines)):
                r1,r2,r3,r4 =(h_lines[h]-pt_rad),(h_lines[h]+pt_rad),(v_lines[v]-pt_rad),(v_lines[v]+pt_rad)
                #cv2.circle(cv_grid_image, (h_lines[h],v_lines[v]),pt_rad,(0,255,0),thickness = 2)
                coords += f"({h}, {v})  ({h_lines[h]}, {v_lines[v]})"
                image_point = cv2.cvtColor(cv_image[r3:r4,r1:r2], cv2.COLOR_BGR2BGRA)
                image_point[:,:,3] = blank_mask[:,:,0]
                cv2.imwrite(os.path.join(pt_path,f"{os.path.split(image)[1].split('.')[0]}_({h},{v})_{h_lines[h]}_{v_lines[v]}_50.png"),image_point)
                if pt_mode:
                    color = cv_mask_image[v_lines[v],h_lines[h]][::-1]
                    coords += f" - ({color})"
                    mask_point = cv2.cvtColor(cv_mask_image[r3:r4,r1:r2], cv2.COLOR_BGR2BGRA)
                    mask_point[:,:,3] = blank_mask[:,:,0]
                    cv2.imwrite(os.path.join(pt_mask_path,f"{os.path.split(image)[1].split('.')[0]}_({h},{v})_{h_lines[h]}_{v_lines[v]}_50.png"),mask_point)
                    result = classify_point(color,model)
                    coords += f" => {result}"
                    class_count.append(result)
                coords += "\n"

        cv2.imwrite(os.path.join(save_path,"lines.png"),cv_graygrid_image)
        cv2.imwrite(os.path.join(save_path,"grid_lines.png"),cv_grid_image)
        cv2.imwrite(os.path.join(save_path,"image_output.png"),cv_image)
        if pt_mode:
            class_types = list(set(class_count))
            class_types.sort()
            for class_type in class_types:
                coords += f"{class_type}: {round(class_count.count(class_type)*100/len(class_count),3)}%\n"
            cv2.imwrite(os.path.join(save_path,"mask_output.png"),cv_mask_image)
        file = open(f"{save_path}/coordinates.txt", "w+")
        file.write(coords)
        file.close()
    except Exception as e:
        msg += "Unable to get points.\n"
    return coords,msg



