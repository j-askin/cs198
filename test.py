import os
from PIL import Image
from pathlib import Path
root_dir = os.path.dirname(__file__)
static = os.path.join(root_dir,"static")
template = os.path.join(root_dir,"templates")
image_dir = os.path.join(static,"images")
model_dir = os.path.join(static,"models")
save_dir = os.path.join(static,"save")


model_list = [""]
model_idx = 0
models_dir = os.path.join(root_dir,model_dir)
if not os.path.exists(models_dir):
    os.mkdir(models_dir)
for folder in os.listdir(models_dir):
    folder_dir = os.path.join(models_dir,folder)
    if os.path.isdir(folder_dir):
        for file in os.listdir(folder_dir):
            if ((os.path.splitext(file)[0]==folder) and (os.path.splitext(file)[1]==".pth") and os.path.isfile(os.path.splitext(os.path.join(folder_dir,file))[0]+".py")):
                model_list.append(os.path.relpath(folder,model_dir).replace("\\","/"))
                break

            if ((os.path.splitext(file)[0]=="folder") and (os.path.splitext(file)[1]==".pth") and os.path.isfile(os.path.splitext(os.path.join(folder_dir,file))[0]+".py")):
                model_list.append(os.path.relpath(folder,model_dir).replace("\\","/"))
                break