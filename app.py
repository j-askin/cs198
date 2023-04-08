from flask import Flask, render_template, Response, request, redirect, url_for
from werkzeug.utils import secure_filename
import sopia
import os
from PIL import Image



class Data:
    #relative paths to file directories
    static = "static"
    template = "templates"
    root_dir = os.path.dirname(__file__)
    image_dir = os.path.join(static,"images")
    model_dir = os.path.join(static,"models")
    save_dir = os.path.join(static,"save")

    def __init__(self):
        #default relative image and model paths
        self.img = "test/test.jpg"
        self.grid_img = "test/test_grid.png"
        self.mask_img = "test/test_seg.png"
        self.config = "test/mask_test.py"
        self.pth = "test/mask_test.pth"

        self.image_idx, self.model_idx = 0,0 #indices of current image and model
        self.image_list, self.model_name_list = [""],[""] #contains relative paths to directories
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
        image_dir_path = os.path.join(self.root_dir,self.image_dir)
        if not os.path.exists(image_dir_path):
            os.mkdir(image_dir_path)
        for root,dirs,files in os.walk(image_dir_path):
            for file in files:
                if ((os.path.splitext(os.path.join(root,file))[1] in [".png",".jpg",".jpeg"]) and (os.path.splitext(os.path.join(root,file))[0][-5:] not in ["_grid","_mask"])):
                    print(os.path.relpath(image_dir_path,os.path.join(root,file)))
                    self.model_name_list.append(os.path.splitext(os.path.relpath(os.path.join(root,file),image_dir_path))[0])
        print("Images:")
        print(self.image_list)

    def get_models(self):
        self.model_list = [""]
        model_dir_path = os.path.join(self.root_dir,self.model_dir)
        if not os.path.exists(model_dir_path):
            os.mkdir(model_dir_path)
        for root,dirs,files in os.walk(model_dir_path):
            for file in files:
                if ((os.path.splitext(os.path.join(root,file))[1]==".pth") and os.path.isfile(os.path.splitext(os.path.join(root,file))[0]+".py")):
                    print(os.path.relpath(model_dir_path,os.path.join(root,file)))
                    self.model_name_list.append(os.path.splitext(os.path.relpath(os.path.join(root,file),model_dir_path))[0])
        print("Models:")
        print(self.model_name_list)

    #get paths for image and model files to display, assumes paths are correct
    def get_paths(self):
        self.img = os.path.relpath(self.image_list[self.image_idx],self.static).replace("\\","/")
        self.grid_img = os.path.relpath(os.path.splitext(self.image_list[self.image_idx])[0]+"_grid.png",self.static).replace("\\","/")
        self.mask_img = os.path.relpath(os.path.splitext(self.image_list[self.image_idx])[0]+"_mask.png",self.static).replace("\\","/")

    def clear(self):
        self.img, self.grid_img, self.mask_img, self.config, self.pth = "", "", "", "", ""
        self.image_idx, self.model_idx = 0,0
        self.model = "" #contains currently loaded model
        self.point_text, self.output_text = "",""

    def get_scale(self):
        pass

data = Data()
app = Flask(__name__, template_folder=data.template,static_folder=data.static)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__),"static")
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


@app.route("/sopia/action/",methods=['GET','POST'])
def sopia_action():
    app.logger.info(request.form["action"].split("."))
    if request.method=="POST":
        match request.form["action"].split(".")[0]:
            case "load_image":
                if 'image_file' not in request.files:
                    app.logger.info("No file detected.\n")
                    file = request.files['image_file']
                if file.filename=='':
                    app.logger.info("No file detected.\n")
                if file and ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in["png","jpg","jpeg"]):
                    file_name = os.path.splitext(os.path.split(secure_filename(file.filename))[1])[0]
                    #remove mask and grid tags
                    if file_name[-5:] in ["_grid","_mask"]:
                        file_name = file_name[:-5]
                    
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'],data.image_dir,file_name,secure_filename(file.filename)))
                
            case "load_model":
                if 'model_file' not in request.files:
                    app.logger.info("No file detected.\n")
                    file = request.files['model_file']
                if file.filename=='':
                    app.logger.info("No file detected.\n")
                if file and ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in["py","pth"]):
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], data.model_dir,secure_filename(file.filename)))
            case "select_image":
                pass
            case "select_grid":
                pass
            case "select_mask":
                pass
            case "select_model":
                pass
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
    data.fix_paths()
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