import glob, os, shutil
import numpy as np
from PIL import Image

def mask_convert(palette,mask_path,out_path,mask_folders,out_folders="",mask_ext=".png",mode='L'):
    if mode not in ['L','RGB']:
        print("Invalid mode. Should be 'L' for colored to gray or 'RGB' for gray to colored\n")
        return
    if len(palette) <= 1:
        print("Palette is empty.")
        return
    #add background color if not already present
    if palette[0] != [0,0,0]:
        palette.insert(0,[0,0,0])
    #convert palette to dict
    if mode == 'L':
        palette_dict = dict(zip([f"[{p[0]} {p[1]} {p[2]}]" for p in palette],range(len(palette)))) #convert palette to dictionary
    elif mode == 'RGB':
        palette_dict = dict(zip(range(len(palette)),[p for p in palette])) #convert palette to dictionary
    #add output folders if not defined
    if len(out_folders) == 0:
        out_folders = mask_folders
    for src_path in [os.path.join(mask_path,mask_folder) for mask_folder in mask_folders]:
        if not os.path.exists(src_path):
            print(f'Dataset mask image folder "{src_path}" does not exist.\n')
            return
    for dest_path in [os.path.join(out_path,mask_folder) for mask_folder in mask_folders]:
        if os.path.exists(dest_path):
            print(f'Output mask directory "{dest_path}" already exists. Removing...\n')
            try:
                shutil.rmtree(dest_path)
            except:
                print('Unable to remove directory "{out_dir}". Please remove it manually.\n')
                return
        os.makedirs(dest_path,exist_ok=True)

    src_path_list = []
    for mask_folder in mask_folders:
        src_path_list.extend(glob.glob(os.path.join(mask_path,mask_folder,f'*{mask_ext}')))
    dest_path_list = [os.path.join(out_path,os.path.relpath(mask_img,mask_path)) for mask_img in src_path_list]
    for ctr in range(len(src_path_list)):
        #convert each image from colored to grayscale format
        img = np.array(Image.open(src_path_list[ctr]).convert('RGB'))
        if mode == 'L':
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    img[i,j] = palette_dict.get(f"[{img[i,j,0]} {img[i,j,1]} {img[i,j,2]}]",0)
        elif mode == 'RGB':
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    img[i,j] = palette_dict.get(img[i,j,0],[0,0,0])
        img = Image.fromarray(img)
        img.save(dest_path_list[ctr])
        print(f"{ctr+1} of {len(src_path_list)} done.")
    print('Done!')

