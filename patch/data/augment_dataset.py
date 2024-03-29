import os,random,shutil
import numpy as np
import albumentations as A
from PIL import Image
import random

def save_img(img,name,dir,mode):
    ext = os.path.splitext(name)[1]
    if ext.upper() == ".JPG":
        ext = ".JPEG"
    img_l,img_w = img.shape[0],img.shape[1]
    abs_path = os.path.join(os.path.dirname(__file__),dir)
    img_s = Image.fromarray(img.astype("uint8"),mode=mode)
    img_s.save(os.path.join(os.path.dirname(__file__),dir,name),ext.upper()[1:])

def process_dir(transform,in_dir,out_dir,raw_dir,mask_dir,ext1,ext2,count):
    print(f"Processing directory {raw_dir}")
    random.seed()
        #check if input and output directories are valid

    
    dir1 = os.path.join(in_dir,raw_dir)
    dir2 = os.path.join(in_dir,mask_dir)
    dir3 = os.path.join(out_dir,raw_dir)
    dir4 = os.path.join(out_dir,mask_dir)
    if not os.path.exists(dir1):
        print(f'Dataset raw image folder "{dir1}" does not exist.\n')
        return
    if not os.path.exists(dir2):
        print(f'Dataset mask image folder "{dir2}" does not exist.\n')
        return
    if os.path.exists(dir3):
        print(f'Output image directory "{dir3}" already exists. Removing...\n')
        try:
            shutil.rmtree(dir3)
        except:
            print(f'Unable to remove directory "{dir3}". Please remove it manually.\n')
            return
    os.makedirs(dir3,exist_ok=True)
    if os.path.exists(dir4):
        print(f'Output mask directory "{dir4}" already exists. Removing...\n')
        try:
            shutil.rmtree(dir4)
        except:
            print(f'Unable to remove directory "{dir4}". Please remove it manually.\n')
            return
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
    print("Processing complete!")

def augment_directory(data_dir = "data",out_dir="sopia_xpl_augmented",
                      train_count = 5, val_count = 5,
                      raw_dir = "raw",raw_train_dir = "train",raw_val_dir = "val",
                      mask_dir = "seg",mask_train_dir = "train",mask_val_dir = "val",
                      raw_train_ext = "_raw.png",raw_val_ext = "_raw.png",
                      mask_train_ext = "_seg.png",mask_val_ext = "_seg.png",
                      root_dir = os.path.dirname(__file__)):
    #generate transformation mask
    transform = A.Compose([
        #flip and randomly scale and rotate the image
        A.Flip(p=0.5),
        A.ShiftScaleRotate(shift_limit=0.625, scale_limit=0.1, rotate_limit=60, interpolation = 3, border_mode = 3, p=1),
    ])
    process_dir(transform,os.path.join(root_dir,data_dir),os.path.join(root_dir,out_dir),os.path.join(raw_dir,raw_train_dir),os.path.join(mask_dir,mask_train_dir),raw_train_ext,mask_train_ext,train_count)
    process_dir(transform,os.path.join(root_dir,data_dir),os.path.join(root_dir,out_dir),os.path.join(raw_dir,raw_val_dir),os.path.join(mask_dir,mask_val_dir),raw_val_ext,mask_val_ext,val_count)
    print(f'Finished generating augmented dataset "{out_dir}"\n')

