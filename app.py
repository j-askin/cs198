from flask import Flask, render_template, Response, request, redirect, url_for
from werkzeug.utils import secure_filename
import sopia
import os
from PIL import Image



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
        self.img = "test/test.jpg"
        self.grid_img = "test/test_grid.png"
        self.mask_img = "test/test_mask.png"
        self.config = "test/seg_test.py"
        self.pth = "test/seg_test.pth"

        self.image_idx, self.model_idx = 0,0 #indices of current image and model
        self.image_list, self.model_list = [""],[""] #contains relative paths to directories
        self.image_count, self.model_count = len(self.image_list),len(self.model_list)
        self.model = "" #contains currently loaded model
        self.point_text, self.output_text = "","" #text to be displayed in output boxes

        #image data
        self.img_w,self.img_l = 0,0

        #image display settings
        self.show_img = True
        self.show_grid = True
        self.show_seg = True
        self.w_scale, self.l_scale = 0, 0
        self.x_off, self.y_off = 0, 0
        self.zoom_level = 1

        #get currently loaded images and models
        self.get_images()
        self.get_models()

    def get_images(self):
        self.image_list = [""]
        self.image_dir = os.path.join(self.root_dir,self.image_dir)
        if not os.path.exists(self.image_dir):
            os.mkdir(self.image_dir)
        for root,dirs,files in os.walk(self.image_dir):
            for file in files:
                file_dir = os.path.join(root,file)
                if ((os.path.splitext(file_dir)[1] in [".png",".jpg",".jpeg"]) and (os.path.splitext(file_dir)[0][-5:] not in ["_grid","_mask"])):
                    print(os.path.relpath(self.image_dir,file_dir))
                    self.image_list.append(os.path.relpath(file_dir,self.image_dir).replace("\\","/"))
        self.image_count = len(self.image_list)
        print("Images:")
        print(self.image_list)

    def get_models(self):
        self.model_list = [""]
        if not os.path.exists(self.model_dir):
            os.mkdir(self.model_dir)
        for root,dirs,files in os.walk(self.model_dir):
            for file in files:
                file_dir = os.path.join(root,file)
                if ((os.path.splitext(file_dir)[1]==".pth") and os.path.isfile(os.path.splitext(file_dir)[0]+".py")):
                    print(os.path.relpath(self.model_dir,file_dir))
                    self.model_list.append(os.path.splitext(os.path.relpath(file_dir,self.model_dir))[0].replace("\\","/"))
        self.model_count = len(self.model_list)
        print("Models:")
        print(self.model_list)

    #get paths for image files to display, assumes paths are correct
    def get_paths(self):
        try:
            self.img = os.path.relpath(os.path.join(self.image_dir,self.image_list[self.image_idx]),self.template).replace("\\","/")
        except:
            pass
        try:
            self.grid_img = (os.path.splitext(os.path.relpath(os.path.join(self.image_dir,self.image_list[self.image_idx]),self.template))[0]+"_grid.png").replace("\\","/")
        except:
            pass
        try:
            self.mask_img = (os.path.splitext(os.path.relpath(os.path.join(self.image_dir,self.image_list[self.image_idx]),self.template))[0]+"_mask.png").replace("\\","/")
        except:
            pass
        try:
            self.config = (os.path.splitext(os.path.relpath(os.path.join(self.model_dir,self.model_list[self.model_idx]),self.template))[0]+".py").replace("\\","/")
        except:
            pass
        try:
            self.pth = (os.path.splitext(os.path.relpath(os.path.join(self.model_dir,self.model_list[self.model_idx]),self.template))[0]+".pth").replace("\\","/")
        except:
            pass


    def update_image(self,image_name):
        try:
            self.get_images()
            self.image_idx = self.image_list.index(image_name)
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



@app.route("/")
@app.route("/sopia/")
def open_sopia():
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
    return render_template("sopia.html",data=data)

@app.route("/sopia/upload/",methods=['GET','POST'])
def sopia_upload():
    app.logger.info("Uploading file!")
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
    app.logger.info(request.form["action"].split("."))
    data.output_text = ""
    if request.method=="POST":
        match request.form["upload"]:
            case "upload_images":
                image_file,image_name = get_file("image_file",["png","jpg","jpeg"])
                grid_file,grid_name = get_file("grid_file",["png"])
                mask_file,mask_name = get_file("mask_file",["png"])
                #ensure image file exists before loading others
                if not (image_file in ["",None] or image_name in ["",None]):
                    #correct invalid file names
                    if os.splitext(image_name)[0][-5:] in ["_grid","_mask"]:
                        image_name = os.splitext(image_name)[0][:-5]+os.splitext(image_name)[1]
                    #override grid and mask names
                    grid_name = os.splitext(image_name)[0]+"_grid"+os.splitext(image_name)[1]
                    mask_name = os.splitext(image_name)[0]+"_mask"+os.splitext(image_name)[1]

                    if sopia.verify_path(data.image_dir,os.splitext(image_name)[0]):
                        image_file.save(os.path.join(data.image_dir,os.splitext(image_name)[0],image_name))
                        print(f"Saved image to {os.path.join(data.image_dir,os.splitext(image_name)[0],image_name)}")
                        if not (grid_file in ["",None]):
                            grid_file.save(os.path.join(data.image_dir,os.splitext(image_name)[0],grid_name))
                            print(f"Saved grid to {os.path.join(data.image_dir,os.splitext(image_name)[0],grid_name)}")
                        if not (mask_file in ["",None]):
                            mask_file.save(os.path.join(data.image_dir,os.splitext(image_name)[0],mask_name))
                            print(f"Saved mask to {os.path.join(data.image_dir,os.splitext(image_name)[0],mask_name)}")
                        #reload image list and select new image
                        app.logger.info(os.path.join(os.splitext(image_name)[0],image_name))
                        data.update_image(os.path.join(os.splitext(image_name)[0],image_name))
                        app.logger.info(data.image_idx)
            case "upload_model":
                config_file,config_name = get_file("config_file",["py"])
                path_file,path_name = get_file("path_file",["pth"])
                #ensure both config and path exist
                if not (config_file in ["",None] or config_name in ["",None] or path_file in ["",None] or path_name in ["",None]):
                    #correct invalid file names, prioritize config filename
                    path_name = os.splitext(config_name)[0]+".pth"
                    if sopia.verify_path(data.model_dir):
                        config_file.save(os.path.join(data.model_dir,os.splitext(config_name)[0],config_name))
                        print(f"Saved config to {os.path.join(data.model_dir,os.splitext(config_name)[0],config_name)}")
                        path_file.save(os.path.join(data.model_dir,os.splitext(config_name)[0],path_name))
                        print(f"Saved paths to {os.path.join(data.model_dir,os.splitext(config_name)[0],path_name)}")
                        #reload model list and select new model
                        app.logger.info(os.path.join(os.splitext(config_name)[0],config_name))
                        data.update_model(os.path.join(os.splitext(config_name)[0],config_name))
                        app.logger.info(data.model_idx)
                        data.model = sopia.get_model(data.static,data.config,data.pth)

@app.route("/sopia/action/",methods=['GET','POST'])
def sopia_action():
    app.logger.info("Performing action!")
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
    app.logger.info("Action requested:\n")
    app.logger.info(request.form["action"].split(".")[0])
    data.output_text = ""
    if request.method=="POST":
        match request.form["action"].split(".")[0]:
            case "update_image":
                app.logger.info("Image requested")
                app.logger.info(request.form["image"])
                data.update_image(request.form["image"])
                app.logger.info(data.image_idx)
            case "update_model":
                app.logger.info("Model requested")
                app.logger.info(request.form["model"])
                data.update_model(request.form["model"])
                app.logger.info(data.model_idx)
            case "clear_data":
                data.clear()
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
            case "get_points":
                img = pt_rad = data.image_list[data.image_idx]
                grid_img = os.path.splitext(data.image_list[data.image_idx])[0]+"_grid.png"
                mask_img = os.path.splitext(data.image_list[data.image_idx])[0]+"_mask.png"
                data.image_list[data.image_idx]
                data.point_text,data.output_text = sopia.get_points(data.root_dir,img,grid_img,mask_img,data.model,pt_rad)
            case _:
                pass
    data.get_paths()
    
    app.logger.info(data.img)
    app.logger.info(data.grid_img)
    app.logger.info(data.mask_img)
    app.logger.info(data.config)
    app.logger.info(data.pth)
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