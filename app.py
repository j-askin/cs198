from flask import Flask, render_template, Response, request, redirect, url_for
from werkzeug.utils import secure_filename
import sopia
import os
from PIL import Image
from pathlib import Path
import glob


class Data:
    #relative paths to file directories
    root_dir = os.path.dirname(__file__)
    static = os.path.join(root_dir,"static")
    template = os.path.join(root_dir,"templates")
    image_dir = os.path.join(static,"images")
    model_dir = os.path.join(static,"models")
    save_dir = os.path.join(static,"save")

    def __init__(self):
        #default relative image and model paths
        self.img = "images/test/test.png"
        self.grid_img = "images/test/grid/test.grid.png"
        self.mask_img = "images/test/mask/test.mask.png"
        self.config = "models/mask_test/mask_test.py"
        self.pth = "models/mask_test/mask_test.pth"

        #Lists containing image and model paths. Does not include the empty option.
        self.image_idx, self.grid_idx, self.mask_idx, self.model_idx = 0,0,0,0 #indices of current image and model
        self.image_list, self.grid_list, self.mask_list, self.model_list = [""],{"":[""]},{"":[""]},[""] #contains relative paths to directories. First entry is always empty.
        self.model = "" #contains currently loaded model
        self.point_text, self.output_text = "","" #text to be displayed in output boxes

        #image data
        self.img_w,self.img_l = 0,0

        #image display settings
        self.show_img = True
        self.show_grid = True
        self.show_mask = True
        self.w_scale, self.l_scale = 0, 0
        self.x_off, self.y_off = 0, 0
        self.zoom_level = 1

        #get currently loaded images and models
        self.get_images()
        self.get_models()

        #test data
        self.image_idx = 0
        self.mask_idx = 0
        self.grid_idx = 0
        self.model_idx = 0

        self.get_paths()

    def get_images(self):
        self.image_list = [""]
        self.grid_list = {"":[""]}
        self.mask_list = {"":[""]}
        self.image_idx, self.grid_idx, self.mask_idx = 0,0,0
        images_dir = os.path.join(self.root_dir,self.image_dir)
        if not os.path.exists(images_dir):
            os.mkdir(images_dir)
        for folder in os.listdir(images_dir):
            folder_dir = os.path.join(images_dir,folder)
            if os.path.isdir(folder_dir):
                for file in os.listdir(folder_dir):
                    if os.path.isfile(os.path.join(folder_dir,file)) and os.path.splitext(file)[1] in [".png",".jpg",".jpeg"]: # and os.path.splitext(file)[0] == folder
                        #add image and all masks and grids saved
                        image = os.path.relpath(folder_dir,self.image_dir).replace("\\","/")
                        self.image_list.append("images/" + os.path.join(folder,file).replace("\\","/"))
                        self.grid_list[folder]=[""]
                        self.mask_list[folder]=[""]
                        grids_dir = os.path.join(folder_dir,"grid")
                        masks_dir = os.path.join(folder_dir,"mask")
                        if not os.path.exists(grids_dir):
                            os.mkdir(grids_dir)
                        if not os.path.exists(os.path.join(folder_dir,"mask")):
                            os.mkdir(masks_dir)
                        for grid in os.listdir(grids_dir):
                            if os.path.isfile(os.path.join(grids_dir,grid)) and os.path.splitext(grid)[1] == ".png" and os.path.splitext(os.path.splitext(grid)[0])[1] == ".grid":
                                self.grid_list[folder].append(grid)
                        for mask in os.listdir(masks_dir):
                            if os.path.isfile(os.path.join(masks_dir,mask)) and os.path.splitext(mask)[1] == ".png" and os.path.splitext(os.path.splitext(mask)[0])[1] == ".mask":
                                self.mask_list[folder].append(mask)
        self.image_list.sort()
        print("Images:")
        for image in self.image_list:
            print(image)
        else:
            folder = os.path.split(os.path.split(image)[0])[1]
            print(f"Grids of {folder}:")
            print(self.grid_list[folder])
            print(f"Masks of {folder}:")
            print(self.mask_list[folder])


    def get_models(self):
        self.model_list = [""]
        self.model_idx = 0
        models_dir = os.path.join(self.root_dir,self.model_dir)
        if not os.path.exists(models_dir):
            os.mkdir(models_dir)
        for folder in os.listdir(models_dir):
            folder_dir = os.path.join(models_dir,folder)
            if os.path.isdir(folder_dir):
                for file in os.listdir(folder_dir):
                    if ((os.path.splitext(file)[0]==folder) and (os.path.splitext(file)[1]==".pth") and os.path.isfile(os.path.splitext(os.path.join(folder_dir,file))[0]+".py")):
                        #                               ^   I think this will return False everytime
                        #                                   not sure if this is supposed to be "file" instead
                        #                                   if it is, then change to "file"
                        #                                   if it's supposed to be "folder", change this to os.path.split(os.path.split(file)[0])[1] == folder
                        self.model_list.append(os.path.relpath(os.path.join(folder_dir,file),self.model_dir).replace("\\","/"))
        self.model_list.sort()
        print("Models:")
        print(self.model_list)

    #get paths for image files to display, assumes paths are correct
    def get_paths(self):
            self.img = os.path.relpath(os.path.join(self.image_dir,self.image_list[self.image_idx]),self.template).replace("\\","/")
            grids = self.grid_list[os.path.split(os.path.split(self.image_list[self.image_idx])[0])[1]]
            masks = self.mask_list[os.path.split(os.path.split(self.image_list[self.image_idx])[0])[1]]
            if (self.grid_idx >= len(grids)):
                self.grid_idx = 0
            if (self.mask_idx >= len(masks)):
                self.mask_idx = 0
            print("Models:")
            print(self.model_list)
            # print(self.grid_list[os.path.split(os.path.split(self.image_list[self.image_idx])[0])[1]][self.grid_idx])
            # exit()
            self.grid_img = os.path.relpath(os.path.join(self.image_dir,os.path.split(os.path.split(self.image_list[self.image_idx])[0])[1],"grid",self.grid_list[os.path.split(os.path.split(self.image_list[self.image_idx])[0])[1]][self.grid_idx]),self.template).replace("\\","/")
            self.mask_img = os.path.relpath(os.path.join(self.image_dir,os.path.split(os.path.split(self.image_list[self.image_idx])[0])[1],"mask",self.mask_list[os.path.split(os.path.split(self.image_list[self.image_idx])[0])[1]][self.mask_idx]),self.template).replace("\\","/")
            self.config = (os.path.splitext(os.path.relpath(os.path.join(self.model_dir,self.model_list[self.model_idx]),self.template))[0]+".py").replace("\\","/")
            self.pth = (os.path.splitext(os.path.relpath(os.path.join(self.model_dir,self.model_list[self.model_idx]),self.template))[0]+".pth").replace("\\","/")
            print(self.img)
            print(self.grid_img)
            print(self.mask_img)
            print(self.config)
            print(self.pth)
            
    def update_image(self,image_name):
        try:
            self.get_images()
            self.image_idx = self.image_list.index(image_name)
            self.img = self.image_list[self.image_idx]
        except ValueError:
            print(f"No such image {image_name} exists.")
        self.image_count = len(self.image_list)

    def update_model(self,model_name):
        try:
            self.get_models()
            self.model_idx = self.model_list.index(model_name)
        except ValueError:
            print(f"No such model {model_name} exists.")
        self.model_count = len(self.model_list)

    def clear(self):
        if self.image_idx == 0: #clear all images in directory
            pass #implement this
        else: #clear only selected image
            pass #implement this
        if self.model_idx == 0: #clear all models in directory
            pass #implement this
        else: #clear only selected model
            pass #implement this
        self.img, self.grid_img, self.mask_img, self.config, self.pth = "", "", "", "", ""
        self.model = "" #contains currently loaded model
        self.image_idx, self.model_idx = 0,0
        self.get_images()
        self.get_models()
        self.point_text, self.output_text = "",""

    def get_scale(self):
        pass

data = Data()
app = Flask(__name__, template_folder=data.template,static_folder=data.static)
app.config['UPLOAD_FOLDER'] = data.static
import logging
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.INFO)

def debug_mes():
    app.logger.info("Request\n")
    app.logger.info(request)
    app.logger.info("Data\n")
    app.logger.info(request.data)
    app.logger.info("Values\n")
    app.logger.info(request.values)
    app.logger.info("Form\n")
    app.logger.info(request.form)
    app.logger.info("Method\n")
    app.logger.info(request.method)
    app.logger.info("Images\n")
    app.logger.info(data.img)
    app.logger.info(data.grid_img)
    app.logger.info(data.mask_img)
    app.logger.info("Configs\n")
    app.logger.info(data.config)
    app.logger.info(data.pth)

def get_file(file_label = "image_file",file_ext = ["png","jpg","jpeg"]):
    file,file_name = "",""
    if file_label not in request.files:
        app.logger.info("No file detected.\n")
    else:
        file = request.files[file_label]
        if file.filename=='':
            app.logger.info("No file detected.\n")
            if file and ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in file_ext):
                file_name = os.path.split(secure_filename(file.filename))[1]
                #remove mask and grid tags
    return file, file_name



@app.route("/")
@app.route("/sopia/")
def open_sopia():
    debug_mes()
    return render_template("sopia.html",data=data)

'''
        '''

@app.route("/sopia/upload/",methods=['GET','POST'])
def sopia_upload():
    data.point_text = ""
    data.output_text = ""
    debug_mes()
    if request.method=="POST":
        match request.form["action"]:
            case "upload_image":
                image_file,image_name = get_file("image_file",["png","jpg","jpeg"])
                if not (image_file in ["",None] or image_name in ["",None]):
                    #correct invalid file names
                    if os.splitext(image_name)[0][-5:] in [".grid",".mask"]:
                        image_name = os.splitext(image_name)[0][:-5]+os.splitext(image_name)[1]
                        if sopia.verify_path(data.image_dir,os.splitext(image_name)[0]):
                            image_file.save(os.path.join(data.image_dir,os.splitext(image_name)[0],image_name))
                            print(f"Saved image to {os.path.join(data.image_dir,os.splitext(image_name)[0],image_name)}")
                            app.logger.info(os.path.join(os.splitext(image_name)[0],image_name))
                            data.update_image(os.path.join(os.splitext(image_name)[0],image_name))
                            app.logger.info(data.image_idx)
                app.logger.info("Image upload")
            case "upload_grid":
                grid_file,grid_name = get_file("grid_file",["png"])
                app.logger.info("Grid upload")
            case "upload_mask":
                mask_file,mask_name = get_file("mask_file",["png"])
                app.logger.info("Mask upload")
            case "upload_model":
                config_file,config_name = get_file("config_file",["py"])
                path_file,path_name = get_file("path_file",["pth"])
                app.logger.info("Model upload")
                if not (config_file in ["",None] or config_name in ["",None] or path_file in ["",None] or path_name in ["",None]):
                    path_name = os.splitext(config_name)[0]+".pth"
                    if sopia.verify_path(data.model_dir):
                        config_file.save(os.path.join(data.model_dir,os.splitext(config_name)[0],config_name))
                        print(f"Saved config to {os.path.join(data.model_dir,os.splitext(config_name)[0],config_name)}")
                        path_file.save(os.path.join(data.model_dir,os.splitext(config_name)[0],path_name))
                        print(f"Saved paths to {os.path.join(data.model_dir,os.splitext(config_name)[0],path_name)}")
                        app.logger.info(os.path.join(os.splitext(config_name)[0],config_name))
                        data.update_model(os.path.join(os.splitext(config_name)[0],config_name))
                        app.logger.info(data.model_idx)
                        data.model = sopia.get_model(data.static,data.config,data.pth)
            case _:
                app.logger.info("Invalid upload")
        data.get_images()
        data.get_models()
        data.get_paths()
    return render_template("sopia.html",data=data)


@app.route("/sopia/update/",methods=['GET','POST'])
def sopia_update():
    data.point_text = ""
    data.output_text = ""
    debug_mes()
    if request.method=="POST":
        match request.form["action"]:
            case "update_image":
                app.logger.info("Image requested")
                app.logger.info(request.form["image"])
                data.update_image(request.form["image"])
                app.logger.info(data.image_idx)
            case "update_grid":
                app.logger.info("Grid requested")
                app.logger.info(request.form["grid"])
                data.update_image(request.form["grid"])
                app.logger.info(data.image_idx)
            case "update_mask":
                app.logger.info("Mask requested")
                app.logger.info(request.form["mask"])
                data.update_image(request.form["mask"])
                app.logger.info(data.image_idx)
            case "update_model":
                app.logger.info("Model requested")
                app.logger.info(request.form["model"])
                data.update_model(request.form["model"])
                app.logger.info(data.model_idx)
            case _:
                print("Invalid update")
    return render_template("sopia.html",data=data)



@app.route("/sopia/create/",methods=['GET','POST'])
def sopia_create():
    data.point_text = ""
    data.output_text = ""
    debug_mes()
    if request.method=="POST":
        match request.form["action"]:
            case "create_mask":
                data.mask_img,data.output_text = sopia.segment_image(data.root_dir,data.image_list[data.image_idx],data.model)
            case "create_grid":
                row_count = request.form["row_count"]
                col_count = request.form["col_space"]
                row_space = request.form["row_space"]
                col_space = request.form["col_space"]
                grid_x = request.form["grid_x"]
                grid_y = request.form["grid_y"]
                #override image size and grid path with that of sample
                if os.path.isfile(data.img):
                    with Image.open(data.img) as im:
                        grid_w,grid_l = im.size()
                else:
                    grid_w = request.form["grid_w"]
                    grid_l = request.form["grid_l"]
                grid_path = os.path.relpath(os.path.splitext(data.image_list[data.image_idx])[0]+"_grid.png",data.static).replace("\\","/")
                data.grid_img,data.output_text = sopia.create_grid(data.root_dir,grid_path,row_count,col_count,row_space,col_space,grid_w,grid_l,grid_x,grid_y)
            case "create_points":
                img = pt_rad = data.image_list[data.image_idx]
                grid_img = os.path.splitext(data.image_list[data.image_idx])[0]+"_grid.png"
                mask_img = os.path.splitext(data.image_list[data.image_idx])[0]+"_mask.png"
                data.image_list[data.image_idx]
                data.point_text,data.output_text = sopia.get_points(data.root_dir,img,grid_img,mask_img,data.model,pt_rad)
            case _:
                print("Invalid create")
    data.get_paths()
    return render_template("sopia.html",data=data)



@app.route("/sopia/compare/points/",methods=['GET','POST'])
def sopia_compare_points():
    print("Comparing Points!")
    debug_mes()
    return render_template("sopia.html",data=data)

@app.route("/sopia/clear/",methods=['GET','POST'])
def sopia_clear():
    print("Clearing Data!")
    data.clear()
    debug_mes()
    return render_template("sopia.html",data=data)





@app.route("/sopia/upload/image/",methods=['GET','POST'])
def sopia_upload_image():
    print("Uploading Image!")
    sopia_upload()

@app.route("/sopia/upload/grid/",methods=['GET','POST'])
def sopia_upload_grid():
    print("Uploading Grid!")
    sopia_upload()

@app.route("/sopia/upload/mask/",methods=['GET','POST'])
def sopia_upload_mask():
    print("Uploading Mask!")
    sopia_upload()

@app.route("/sopia/upload/model/",methods=['GET','POST'])
def sopia_upload_model():
    print("Uploading Model!")
    sopia_upload()

@app.route("/sopia/update/image/",methods=['GET','POST'])
def sopia_update_image():
    print("Updating Image!")
    sopia_update()
    return render_template("sopia.html", data=data)

@app.route("/sopia/update/grid/",methods=['GET','POST'])
def sopia_update_grid():
    print("Updating Grid!")
    sopia_update()

@app.route("/sopia/update/mask/",methods=['GET','POST'])
def sopia_update_mask():
    print("Updating Mask!")
    sopia_update()

@app.route("/sopia/update/model/",methods=['GET','POST'])
def sopia_update_model():
    print("Updating Model!")
    return render_template("sopia.html",data=data)

@app.route("/sopia/create/grid/",methods=['GET','POST'])
def sopia_create_grid():
    print("Creating Grid!")
    sopia_create()

@app.route("/sopia/create/mask/",methods=['GET','POST'])
def sopia_create_mask():
    print("Creating Mask!")
    sopia_create()

@app.route("/sopia/create/points/",methods=['GET','POST'])
def sopia_create_points():
    print("Creating Points!")
    sopia_create()








'''
        case "load_image":
            img_path = request.form['image_path']
            data.img,data.output_text = sopia.load_image(os.path.join(data.static,img_path))
            #automatically generate a default grid of 5 rows and columns, centered on the sample
            with Image.open(data.img) as im:
                x_size,y_size = im.size
                app.logger.info(x_size//6)
                app.logger.info(y_size//6)
                h_space,v_space = x_size//6,y_size//6
            data.grid_img,data.output_text = sopia.create_grid(os.path.join(data.static,"sample/auto_grid.png"),5,h_space,5,v_space,x_size, h_space,y_size, v_space)

        case "load_grid":
            grid_path = request.form['grid_path']
            data.grid_img,data.output_text = sopia.load_image(os.path.join(data.static,grid_path))
        case "load_mask":
            mask_path = request.form['mask_path']
            data.mask_img,data.output_text = sopia.load_image(os.path.join(data.static,mask_path))
        case "load_model":
            config_path = request.form['mask_mdl_path']+".py"
            pth_path = request.form['mask_mdl_path']+".pth"
            data.config, data.pth, data.mask_mdl, data.output_text = sopia.load_model(os.path.join(data.mdl_dir,config_path),(os.path.join(data.mdl_dir,pth_path)))
            app.logger.info("Data")
            app.logger.info(data.config)
            app.logger.info(data.pth)
'''

if __name__ == "__main__":
    app.run(debug=True)