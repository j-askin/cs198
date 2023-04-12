import os,sys,random
import numpy as np
import albumentations as A
from PIL import Image
import datetime
import random
import cv2


root_dir = os.path.dirname(__file__)
#default argument values
data_dir = "data"
raw_dir = "raw"
raw_train_dir = "train"
raw_val_dir = "val"
mask_dir = "seg"
mask_train_dir = "train"
mask_val_dir = "val"
raw_train_ext = "_raw.png"
raw_val_ext = "_raw.png"
mask_train_ext = "_seg.png"
mask_val_ext = "_seg.png"
train_count = 20
val_count = 5
data_dir="sopia"
out_dir="data/sopia"


def remove_box(image):
    return image #implement this later

transform = A.Compose([
    #flip and rotate the image
    A.RandomRotate90(p=0.5),
    A.Flip(p=0.5),
    A.Transpose(p=0.5),
    #shrink and/or shift the image
    A.OneOf([
        A.ShiftScaleRotate(shift_limit=0.5, scale_limit=0.1, rotate_limit=45, interpolation = 3, border_mode = 3, p=0.5),
        A.ShiftScaleRotate(shift_limit=0.625, scale_limit=0.1, rotate_limit=45, interpolation = 3, border_mode = 4, p=0.5),
    ],p=0.6),
    #crop random parts of the image borders
    A.RandomCropFromBorders(crop_left=0.2, crop_right=0.2, crop_top=0.2, crop_bottom=0.2,p=1.0),
    #sharpen the image
    A.Sharpen(alpha=(0.5,1.0),lightness=(0.5,1.0),p=0.6),
    #change the lighting
    A.OneOf([
        A.RandomBrightnessContrast(brightness_limit=0.3,contrast_limit=0.3,p=1.0),
        A.RandomGamma(gamma_limit=(75,125),p=1.0),
    ],p=0.6),
    #damage the image
    A.PixelDropout(dropout_prob=0.01,p=0.05),
])

def save_img(img,name,dir,mode):
    ext = os.path.splitext(name)[1]
    if ext.upper() == ".JPG":
        ext = ".JPEG"
    img_l,img_w = img.shape[0],img.shape[1]
    abs_path = os.path.join(os.path.dirname(__file__),dir)
    img_s = Image.fromarray(img.astype("uint8"),mode=mode)
    img_s.save(os.path.join(os.path.dirname(__file__),dir,name),ext.upper()[1:])

def process_dir(in_dir,out_dir,raw_dir,mask_dir,ext1,ext2,count):
    print(f"Processing directory {raw_dir}")
    random.seed()
    dir1 = os.path.join(in_dir,raw_dir)
    dir2 = os.path.join(in_dir,mask_dir)
    dir3 = os.path.join(out_dir,raw_dir)
    dir4 = os.path.join(out_dir,mask_dir)

    if not os.path.exists(dir1):
        return
    if not os.path.exists(dir2):
        return
    os.makedirs(dir3,exist_ok=True)
    os.makedirs(dir4,exist_ok=True)
    files_1, files_2 = [],[]
    for root,_,files in os.walk(dir1):
        for name in files:
            files_1.append(os.path.relpath(os.path.join(root,name),dir1))
    for root,_,files in os.walk(dir2):
        for name in files:
            files_2.append(os.path.relpath(os.path.join(root,name),dir2))

    files_1 = [file_1 for file_1 in files_1 if file_1.endswith(ext1)]
    files_2 = [file_2 for file_2 in files_2 if file_2.endswith(ext2)]

    files_1s = [f_1.removesuffix(ext1) for f_1 in files_1]
    files_2s = [f_2.removesuffix(ext2) for f_2 in files_2]
    files_1 = [file_1 for file_1 in files_1 if file_1.removesuffix(ext1) in files_2s]
    files_2 = [file_2 for file_2 in files_2 if file_2.removesuffix(ext2) in files_1s]

    if (len(files_1s) != len(set(files_1s))) or (len(files_2s) != len(set(files_2s)) or len(files_1) != len(files_2)):
        return
    files_1.sort()
    files_2.sort()
    print(f"Files obtained.")
    #Processing stage
    for i in range(len(files_1)):
        image_path = os.path.join(dir1,files_1[i])
        mask_path = os.path.join(dir2,files_2[i])
        image_out_path,image_out_name = os.path.split(os.path.join(dir3,files_1[i]))
        mask_out_path,mask_out_name = os.path.split(os.path.join(dir4,files_2[i]))

        image_load = Image.open(image_path)
        mask_load = Image.open(mask_path)
        image_mode = image_load.mode
        mask_mode = mask_load.mode
        image = np.array(image_load.convert("RGB"))
        image = remove_box(image)
        mask = np.array(mask_load)
        #save originals
        print(f"Processing file {files_1[i]}-{0}")
        save_img(image,image_out_name,image_out_path,image_mode)
        save_img(mask,mask_out_name,mask_out_path,mask_mode)
        #save transforms
        for c in range(1,count+1):
            print(f"Processing file {files_1[i]}-{c}")
            image_out_name_t = f'_{c}'.join(os.path.splitext(image_out_name))
            mask_out_name_t = f'_{c}'.join(os.path.splitext(mask_out_name))
            val_s = transform(image=image,mask=mask)
            image_s = val_s['image']
            mask_s = val_s['mask']
            save_img(image_s,image_out_name_t,image_out_path,image_mode)
            save_img(mask_s,mask_out_name_t,mask_out_path,mask_mode)



process_dir(os.path.join(root_dir,data_dir),os.path.join(root_dir,out_dir),os.path.join(raw_dir,raw_train_dir),os.path.join(mask_dir,mask_train_dir),raw_train_ext,mask_train_ext,train_count)
process_dir(os.path.join(root_dir,data_dir),os.path.join(root_dir,out_dir),os.path.join(raw_dir,raw_val_dir),os.path.join(mask_dir,mask_val_dir),raw_val_ext,mask_val_ext,val_count)

