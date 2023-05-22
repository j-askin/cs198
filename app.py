from flask import Flask, flash, render_template, Response, request, redirect, url_for
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
        self.points = sopia.Points() #list of points
        self.point_classes = []
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

        #self.get_paths()

    def get_images(self):
        self.image_list = [""]
        self.grid_list = {"":[""]}
        self.mask_list = {"":[""]}
        self.image_idx, self.grid_idx, self.mask_idx = self.image_idx, self.grid_idx, self.mask_idx
        images_dir = os.path.join(self.root_dir,self.image_dir)
        if not os.path.exists(images_dir):
            os.makedirs(images_dir,exist_ok=True)
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
                            os.makedirs(grids_dir,exist_ok=True)
                        if not os.path.exists(os.path.join(folder_dir,"mask")):
                            os.makedirs(masks_dir,exist_ok=True)
                        for grid in os.listdir(grids_dir):
                            if os.path.isfile(os.path.join(grids_dir,grid)) and os.path.splitext(grid)[1] == ".png" and os.path.splitext(os.path.splitext(grid)[0])[1] == ".grid":
                                self.grid_list[folder].append(folder + "/grid/" + grid)
                        for mask in os.listdir(masks_dir):
                            if os.path.isfile(os.path.join(masks_dir,mask)) and os.path.splitext(mask)[1] == ".png" and os.path.splitext(os.path.splitext(mask)[0])[1] == ".mask":
                                self.mask_list[folder].append(folder + "/mask/" + mask)
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
        self.model_idx = self.model_idx
        models_dir = os.path.join(self.root_dir,self.model_dir)
        if not os.path.exists(models_dir):
            os.makedirs(models_dir,exist_ok=True)
        for folder in os.listdir(models_dir):
            folder_dir = os.path.join(models_dir,folder)
            if os.path.isdir(folder_dir):
                print("Models present")
                for file in os.listdir(folder_dir):
                    print(file)
                    if ((os.path.splitext(file)[0]==folder) and (os.path.splitext(file)[1]==".pth") and os.path.isfile(os.path.splitext(os.path.join(folder_dir,file))[0]+".py")):
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
        self.grid_img = os.path.relpath(os.path.join(self.image_dir,os.path.split(os.path.split(self.image_list[self.image_idx])[0])[1],"grid",self.grid_list[os.path.split(os.path.split(self.image_list[self.image_idx])[0])[1]][self.grid_idx]),self.template).replace("\\","/")
        self.mask_img = os.path.relpath(os.path.join(self.image_dir,os.path.split(os.path.split(self.image_list[self.image_idx])[0])[1],"mask",self.mask_list[os.path.split(os.path.split(self.image_list[self.image_idx])[0])[1]][self.mask_idx]),self.template).replace("\\","/")
        self.config = (os.path.splitext(os.path.relpath(os.path.join(self.model_dir,self.model_list[self.model_idx]),self.template))[0]+".py").replace("\\","/")
        self.pth = (os.path.splitext(os.path.relpath(os.path.join(self.model_dir,self.model_list[self.model_idx]),self.template))[0]+".pth").replace("\\","/")
            
    def update_image(self,image_name):
        try:
            self.get_images()
            self.image_idx = self.image_list.index(image_name)
            self.img = self.image_list[self.image_idx]
        except ValueError:
            print(f"No such image {image_name} exists.")
        self.image_count = len(self.image_list)

    def update_grid(self,grid_name):
        try:
            self.get_images()
            self.grid_idx = self.grid_list[grid_name.split("/")[0]].index(grid_name)
            self.grid_img = "images/" + self.grid_list[grid_name.split("/")[0]][self.grid_idx]
        except ValueError:
            print(f"No such image {grid_name} exists.")
        self.grid_count = len(self.grid_list[grid_name.split("/")[0]])


    def update_mask(self,mask_name):
        try:
            self.get_images()
            self.mask_idx = self.mask_list[mask_name.split("/")[0]].index(mask_name)
            self.mask_img = "images/" + self.mask_list[mask_name.split("/")[0]][self.mask_idx]
        except ValueError:
            print(f"No such image {mask_name} exists.")
        self.mask_count = len(self.mask_list[mask_name.split("/")[0]])


    def update_model(self,model_name):
            self.get_models()
            print(self.model_list)
            print(model_name)
            self.model_idx = self.model_list.index(model_name)
            self.config = "models/" + self.model_list[self.model_idx].split(".")[0] + ".py"
            self.pth = "models/" + self.model_list[self.model_idx].split(".")[0] + ".pth"
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
        self.points = sopia.Points()

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

@app.route("/")
@app.route("/sopia/")
def open_sopia():
    debug_mes()
    return render_template("sopia.html",data=data)


def get_file(file_label = "image_file",file_path = "static/images", file_ext = ["png","jpg","jpeg"]):
    if file_label not in request.files:
        flash(f'No file detected.')
        return redirect(request.url)
    else:
        file = request.files[file_label]
        if file.filename == '':
            flash('No selected file')
            return render_template("sopia.html",data=data)
        if file and file.filename.split(".")[-1].lower() in file_ext:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(file_path,"uploads").replace("\\", "/")
            if (len(filename.split(".")) == 3):
                upload_folder = os.path.join(upload_folder,filename.split(".")[1])
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder,exist_ok=True)
            file.save(os.path.join(upload_folder,filename))


def get_model(config_label = "config_file",path_label = "path_file", model_path = "static/models"):
    if config_label not in request.files:
        flash(f'No config file detected.')
        return redirect(request.url)
    elif path_label not in request.files:
        flash(f'No path file detected.')
        return redirect(request.url)
    else:
        config_file,path_file = request.files[config_label],request.files[path_label]
        if config_file.filename == '' or path_file.filename == '':
            flash('No selected config or path file')
            return render_template("sopia.html",data=data)
        if config_file and config_file.filename.split(".")[-1].lower() == "py" and path_file and path_file.filename.split(".")[-1].lower() == "pth":
            config_filename = secure_filename(config_file.filename)
            path_filename = secure_filename(path_file.filename)
            upload_folder = os.path.join(model_path,config_filename.split(".")[0])
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder,exist_ok=True)
            config_file.save(os.path.join(upload_folder,config_filename))
            path_file.save(os.path.join(upload_folder,path_filename))

@app.route("/sopia/upload/",methods=['GET','POST'])
def sopia_upload():
    data.point_text = ""
    data.output_text = ""
    debug_mes()
    if request.method=="POST":
        match list(request.form.keys())[0]:
            case "upload_image":
                get_file('image_file',data.image_dir,["png","jpg","jpeg"])
                app.logger.info("Image upload")
            case "upload_grid":
                get_file('grid_file',data.image_dir,["png"])
                app.logger.info("Grid upload")
            case "upload_mask":
                get_file('mask_file',data.image_dir,["png"])
                app.logger.info("Mask upload")
            case "upload_model":
                get_model('config_file','path_file')
                app.logger.info("Model upload")
            case _:
                app.logger.info(f"Invalid upload {list(request.form.keys())[0]}")
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
                data.update_grid(request.form["grid"])
                app.logger.info(data.image_idx)
            case "update_mask":
                app.logger.info("Mask requested")
                app.logger.info(request.form["mask"])
                data.update_mask(request.form["mask"])
                app.logger.info(data.image_idx)
            case "update_model":
                app.logger.info("Model requested")
                app.logger.info(request.form["model"])
                data.update_model(request.form["model"])
                app.logger.info(data.model_idx)
            case _:
                print(f"Invalid update {request.form['action']}")
    return render_template("sopia.html",data=data)



@app.route("/sopia/create/",methods=['GET','POST'])
def sopia_create():
    data.point_text = ""
    data.output_text = ""
    debug_mes()
    app.logger.info("Create requested")
    app.logger.info(data.image_list[data.image_idx])
    app.logger.info(data.image_idx)
    app.logger.info(data.image_list)
    if request.method=="POST":
        match request.form["action"]:
            case "create_mask":
                app.logger.info("Mask requested")
                mask_name = request.form["mask_name"]
                mask_img = os.path.split(data.image_list[data.image_idx])[0]+"/mask/"+mask_name+".mask.png"
                data.model = sopia.load_model(data.static,data.config,data.pth)
                data.mask_img,data.output_text = sopia.segment_image(data.static,mask_img,data.img,data.model)
            case "create_grid":
                row_count = int(request.form["row_count"])
                col_count = int(request.form["col_count"])
                row_space = int(request.form["row_space"])
                col_space = int(request.form["col_space"])
                grid_x = int(request.form["grid_x"])
                grid_y = int(request.form["grid_y"])
                #override image size and grid path with that of sample
                image = data.image_list[data.image_idx]
                if os.path.isfile(image):
                    with Image.open(image) as im:
                        grid_w,grid_l = im.size
                else:
                    grid_w = int(request.form["grid_w"])
                    grid_l = int(request.form["grid_l"])
                grid_name = request.form["grid_name"]
                app.logger.info("Grid requested")
                grid_img = os.path.split(data.image_list[data.image_idx])[0]+"/grid/"+grid_name+".grid.png"
                app.logger.info(data.static)
                app.logger.info(grid_img)
                data.grid_img,data.output_text = sopia.create_grid(data.static,grid_img,row_count,col_count,row_space,col_space,grid_w,grid_l,grid_x,grid_y)
            case "get_points":
                data.model = sopia.load_model(data.static,data.config,data.pth)
                data.points,data.output_text = sopia.get_points(data.static,data.img,data.grid_img,data.mask_img,data.model)
                app.logger.info(data.points.classes)
                data.point_classes = data.points.classes
                data.point_text, _ = data.points.save_points(data.static,"save")
            case _:
                print(f"Invalid create {request.form['action']}")
    return render_template("sopia.html",data=data)



@app.route("/sopia/compare/points/",methods=['GET','POST'])
def sopia_compare_points():
    print("Comparing Points!")
    debug_mes()
    return render_template("sopia.html",data=data)

@app.route("/sopia/update/point",methods=['GET','POST'])
def sopia_update_point():
    print("Updating Point!")
    debug_mes()
    if request.method=="POST":
        match request.form["action"]:
            case "update_point":
                pt_x = int(request.form["pt_x"])
                pt_y = int(request.form["pt_y"])
                pt_class = request.form["pt_class"]
                data.output_text = data.points.update_point(pt_x,pt_y,pt_class)
                data.point_text, _ = data.points.save_points(data.static,"save")
            case _:
                print("Invalid action!")
    return render_template("sopia.html",data=data)

@app.route("/sopia/save/points",methods=['GET','POST'])
def sopia_save_points():
    print("Saving Points To Text!")
    debug_mes()
    data.point_text, path = data.points.save_points(data.static,"save",True,50)
    data.output_text = f"Points have been saved to {path}."
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
    return render_template("sopia.html",data=data)

@app.route("/sopia/upload/grid/",methods=['GET','POST'])
def sopia_upload_grid():
    print("Uploading Grid!")
    sopia_upload()
    return render_template("sopia.html",data=data)

@app.route("/sopia/upload/mask/",methods=['GET','POST'])
def sopia_upload_mask():
    print("Uploading Mask!")
    sopia_upload()
    return render_template("sopia.html",data=data)

@app.route("/sopia/upload/model/",methods=['GET','POST'])
def sopia_upload_model():
    print("Uploading Model!")
    sopia_upload()
    return render_template("sopia.html",data=data)

@app.route("/sopia/update/image/",methods=['GET','POST'])
def sopia_update_image():
    print("Updating Image!")
    sopia_update()
    return render_template("sopia.html", data=data)

@app.route("/sopia/update/grid/",methods=['GET','POST'])
def sopia_update_grid():
    print("Updating Grid!")
    sopia_update()
    return render_template("sopia.html",data=data)

@app.route("/sopia/update/mask/",methods=['GET','POST'])
def sopia_update_mask():
    print("Updating Mask!")
    sopia_update()
    return render_template("sopia.html",data=data)

@app.route("/sopia/update/model/",methods=['GET','POST'])
def sopia_update_model():
    print("Updating Model!")
    sopia_update()
    return render_template("sopia.html",data=data)

@app.route("/sopia/create/grid/",methods=['GET','POST'])
def sopia_create_grid():
    print("Creating Grid!")
    sopia_create()
    return render_template("sopia.html",data=data)

@app.route("/sopia/create/mask/",methods=['GET','POST'])
def sopia_create_mask():
    print("Creating Mask!")
    sopia_create()
    return render_template("sopia.html",data=data)

@app.route("/sopia/create/points/",methods=['GET','POST'])
def sopia_create_points():
    print("Creating Points!")
    sopia_create()
    return render_template("sopia.html",data=data)







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