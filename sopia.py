import os, cv2, time
from PIL import Image
import numpy as np
from tkinter import filedialog
import mmcv
from mmseg.apis import init_segmentor, inference_segmentor, show_result_pyplot, train_segmentor

def load_image(img_path=""):
    img = ""
    if not os.path.exists(os.path.join(os.path.dirname(__file__),"data")):
        os.mkdir(os.path.join(os.path.dirname(__file__),"data"))
    print(f"Attempting to load image {os.path.join(os.path.dirname(__file__),img_path)}")
    if os.path.isfile(os.path.join(os.path.dirname(__file__),img_path)):
        img = os.path.join(os.path.dirname(__file__),img_path)
        print(f"Loaded image {img}")
    else:
        print("Unable to load image.")
        img = ""
    return img

def load_grid(grid_path=""):
    grid_img = ""
    if not os.path.exists(os.path.join(os.path.dirname(__file__),"data")):
        os.mkdir(os.path.join(os.path.dirname(__file__),"data"))
    print(f"Attempting to load grid image {os.path.join(os.path.dirname(__file__),grid_path)}")
    if os.path.isfile(os.path.join(os.path.dirname(__file__),grid_path)):
        grid_img = os.path.join(os.path.dirname(__file__),grid_path)
        print(f"Loaded grid image {grid_img}")
    else:
        print("Unable to load grid.")
        grid_img = ""
    return grid_img

def load_seg(seg_path=""):
    seg_img = ""
    if not os.path.exists(os.path.join(os.path.dirname(__file__),"data")):
        os.mkdir(os.path.join(os.path.dirname(__file__),"data"))
    print(f"Attempting to load segmented mask {os.path.join(os.path.dirname(__file__),seg_path)}")
    if os.path.isfile(os.path.join(os.path.dirname(__file__),seg_path)):
        seg_img = os.path.join(os.path.dirname(__file__),seg_path)
        print(f"Loaded segmented mask {seg_img}")
    else:
        print("Unable to load segmented mask.")
    return seg_img

def load_model(seg_cfg_path = "",seg_pth_path = ""):
    seg_cfg, seg_pth, seg_mdl = "", "", ""
    if not os.path.exists(os.path.join(os.path.dirname(__file__),"data")):
        os.mkdir(os.path.join(os.path.dirname(__file__),"data"))
    print(f"Attempting to load segmenter config {os.path.join(os.path.dirname(__file__),seg_cfg_path)}")
    if os.path.exists(os.path.join(os.path.dirname(__file__),seg_cfg_path)):
        seg_cfg = os.path.join(os.path.dirname(__file__),seg_cfg_path)
    else:
        print("Unable to load segmenter config.")
    print(f"Attempting to load segmenter path {os.path.join(os.path.dirname(__file__),seg_pth_path)}")
    if os.path.isfile(os.path.join(os.path.dirname(__file__),seg_pth_path)):
        seg_pth = os.path.join(os.path.dirname(__file__),seg_pth_path)
    else:
        print("Unable to load segmenter path.")
    if seg_cfg != "" and seg_pth != "":
        print("Loading segmentation model...")
        try:
            seg_mdl = init_segmentor(seg_cfg, seg_pth, device='cuda:0')
            print("Loaded segmentation model to gpu.")
        except AssertionError as e:
            if e:
                try:
                    seg_mdl = init_segmentor(seg_cfg, seg_pth, device='cpu')
                    print("Loaded segmentation model to cpu.")
                except:
                    print(f"Unable to load model: {e}")
        except Exception as e:
            print(f"Unable to load model: {e}")
    
    return seg_cfg,seg_pth,seg_mdl

def segment_image(img = "", seg_mdl = "", seg_path = "", show=False):
    #Replace hard coded classes pallete with result from labels json file
    seg_img = ""
    if img == "":
        print("Please load an image first.")
    elif seg_mdl in ["",None]:
        print("Please load a model first.")
    else:
        print(f"Segmenting image {img}...")
        try:
            result = inference_segmentor(seg_mdl,img)
            if out_path == "":
                out_path = img[:-4]+"_seg.png"
            if show:
                show_result_pyplot(seg_mdl, img, result, opacity=1, out_file=out_path)
            seg_img = out_path
            print(f"Segmented image generated to {out_path}.")
        except Exception as e:
            print("Unable to segment image: {e}")
    return seg_img

def create_grid(grid_path = "grid.png", v_count = 10,v_space = 200,h_count = 10,h_space = 200,x_size = 3396, x_off = 100, y_size = 2547, y_off = 100):
    grid_height = v_count + (v_count * v_space) - v_space
    grid_width = h_count + (h_count * h_space) - h_space
    img1 = Image.new(mode="RGBA", size=(grid_width, grid_height))
    actual_grid = []
    for i in range(grid_height):
        for j in range(grid_width):
            if i%(v_space+1) == 0 and j%(h_space+1) == 0:
                actual_grid.append((0,255,255,255))
            elif i%(h_space+1) == 0:
                actual_grid.append((255,0,255,255))
            elif j%(h_space+1) == 0:
                actual_grid.append((255,255,0,255))
            else:
                actual_grid.append((0,0,0,0))
    img1.putdata(actual_grid)
    img1.save(os.path.join(os.path.dirname(__file__),out_path+"_overlay.png"), "PNG")
    img2 = Image.new(mode="RGBA", size=(x_size, y_size))
    img2.paste(img1,(x_off,y_off))
    img2.save(os.path.join(os.path.dirname(__file__),out_path), "PNG")
    print(f"Saved grid to {out_path}")
    return os.path.join(os.path.dirname(__file__),out_path)

def classify_point(color = (0,0,0),seg_mdl=""):
    if seg_mdl in ["",None]:
        return ""
    else:
        materials = list(zip(seg_mdl.CLASSES,seg_mdl.PALETTE))
        for material in materials:
            if tuple(color) == tuple(material[1]):
                return material[0]
        return "UNKNOWN MATERIAL"

def get_points(img="",grid_img="",seg_img="",seg_mdl="",pt_rad=25):
    pt_mode = False
    #generate output directory
    #savePath = os.path.join(os.path.expanduser("~"),f"Desktop/SoPIA/cs198/save/{time.strftime('%m%y%d-%H%M%S',time.localtime(time.time()))}")
    savePath = os.path.abspath(os.path.join(os.path.dirname(__file__),f"save/{time.strftime('%m%y%d-%H%M%S',time.localtime(time.time()))}"))
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    pt_path = os.path.join(savePath,"points")
    if not os.path.exists(pt_path):
        os.makedirs(pt_path)
    pt_seg_path = os.path.join(savePath,"segmented")
    if not os.path.exists(pt_seg_path):
        os.makedirs(pt_seg_path)
    #load images
    if os.path.isfile(img):
        cv_img = cv2.imread(img)
    else:
        print("No image found.")
        return
    if os.path.isfile(grid_img):
        cv_grid_img = cv2.imread(grid_img)
    else:
        print("No grid image found.")
        return
    if os.path.isfile(seg_img):
        cv_seg_img = cv2.imread(seg_img)
        if cv_img.shape != cv_grid_img.shape:
            print("Segmenter image sizes do not match.")
            pt_mode = False
        else:
            pt_mode = True
    else:
        print("No segmented image found.")
        pt_mode = False

    if cv_img.shape != cv_grid_img.shape:
        print("Image sizes do not match.")
        return

    img_l,img_w = cv_img.shape[0],cv_img.shape[1]
    cv_gsgrid_img = cv2.cvtColor(cv_grid_img,cv2.COLOR_BGR2GRAY)
    #Hough transform: obtain coordinates of grid intersections
    lines = cv2.HoughLines(cv_gsgrid_img, 1, np.pi/180, 500)
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
        cv2.line(cv_gsgrid_img, pt1, pt2, (255,255,255), 3, cv2.LINE_AA)
    h_lines.sort()
    v_lines.sort()

    #Output all coordinates
    coords = ""
    seg_coords = ""
    class_count = []
    blank_mask = np.zeros((pt_rad*2,pt_rad*2,3), np.uint8)
    cv2.circle(blank_mask, (pt_rad,pt_rad),pt_rad,(255,255,255),thickness = -1)
    coords += "Sample Coordinates:\n"
    seg_coords += "Segmented Coordinates:\n"
    for h in range(len(h_lines)):
        for v in range(len(v_lines)):
            r1,r2,r3,r4 =(h_lines[h]-pt_rad),(h_lines[h]+pt_rad),(v_lines[v]-pt_rad),(v_lines[v]+pt_rad)
            #cv2.circle(cv_grid_img, (h_lines[h],v_lines[v]),pt_rad,(0,255,0),thickness = 2)
            coords += f"({h}, {v})  ({h_lines[h]}, {v_lines[v]})\n"
            img_point = cv2.cvtColor(cv_img[r3:r4,r1:r2], cv2.COLOR_BGR2BGRA)
            img_point[:,:,3] = blank_mask[:,:,0]
            cv2.imwrite(os.path.join(pt_path,f"{os.path.split(img)[1].split('.')[0]}_({h},{v})_{h_lines[h]}_{v_lines[v]}_50.png"),img_point)
            if pt_mode:
                color = cv_seg_img[v_lines[v],h_lines[h]][::-1]
                print(color)
                seg_coords += f"({h}, {v})  ({h_lines[h]}, {v_lines[v]}) ({color})"
                seg_point = cv2.cvtColor(cv_seg_img[r3:r4,r1:r2], cv2.COLOR_BGR2BGRA)
                seg_point[:,:,3] = blank_mask[:,:,0]
                cv2.imwrite(os.path.join(pt_seg_path,f"{os.path.split(img)[1].split('.')[0]}_({h},{v})_{h_lines[h]}_{v_lines[v]}_50.png"),seg_point)
                result = classify_point(color,seg_mdl)
                seg_coords += f" - {result}\n"
                class_count.append(result)


    cv2.imwrite(os.path.join(savePath,"lines.png"),cv_gsgrid_img)
    cv2.imwrite(os.path.join(savePath,"grid_lines.png"),cv_grid_img)
    cv2.imwrite(os.path.join(savePath,"image_output.png"),cv_img)
    file = open(f"{savePath}/coordinates.txt", "w+")
    file.write(coords)
    file.close()
    if pt_mode:
        class_types = list(set(class_count))
        class_types.sort()
        for class_type in class_types:
            print(f"{class_type}: {round(class_count.count(class_type)*100/len(class_count),3)}%")
            seg_coords += f"{class_type}: {round(class_count.count(class_type)*100/len(class_count),3)}%\n"
        cv2.imwrite(os.path.join(savePath,"segmented_output.png"),cv_seg_img)
        file = open(f"{savePath}/seg_coordinates.txt", "w+")
        file.write(seg_coords)
        file.close()

    print(f"Points written to\n{savePath}")
    return coords



