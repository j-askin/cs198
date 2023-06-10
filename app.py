from flask import Flask, flash, render_template, Response, request, redirect, url_for, session
import secrets
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash,generate_password_hash
import concretile
import os
from PIL import Image

def get_file(file_label = "image_file",file_path = "static/images", file_ext = ["png","jpg","jpeg"]):
    if file_label not in request.files:
        flash(f'No file detected.')
        return redirect(request.url)
    else:
        file = request.files[file_label]
        if file.filename == '':
            flash('No selected file')
            return render_template("concretile.html",data=data)
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
            return render_template("concretile.html",data=data)
        if config_file and config_file.filename.split(".")[-1].lower() == "py" and path_file and path_file.filename.split(".")[-1].lower() == "pth":
            config_filename = secure_filename(config_file.filename)
            path_filename = secure_filename(path_file.filename)
            upload_folder = os.path.join(model_path,config_filename.split(".")[0])
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder,exist_ok=True)
            config_file.save(os.path.join(upload_folder,config_filename))
            path_file.save(os.path.join(upload_folder,path_filename))


#initialize the web application
root_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=os.path.join(root_dir,"templates"),static_folder=os.path.join(root_dir,"static"))
app.config['UPLOAD_FOLDER'] = os.path.join(root_dir,"static")
app.config['SECRET_KEY'] = secrets.token_hex()
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(root_dir, 'database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(512))
    password = db.Column(db.String(512))
    def __init__(self,username,password):
        self.username = username
        self.password = password
    def __repr__(self):
        return '<User %r>' % self.username
with app.app_context():
    db.create_all()
data = concretile.Data()


#landing page, redirect to login page
@app.route("/",methods=["GET","POST"])
def home():
    if 'username' in session:
        return redirect(url_for('open_concretile'))
    else:
        return redirect(url_for('login'))

#login page for user authentication
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password,password) or len(password) == 0:
            flash("Invalid username/password.")
            return render_template("login.html")
        else:
            session['username'] = username
            data.user = username
            return redirect(url_for('open_concretile'))
    else:
        return render_template("login.html")

#register page to sign up for a new account
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists. Please try again.")
            return render_template("register.html")
        elif len(password) == 0:
            flash("Invalid password. Please try again.")
            return render_template("register.html")
        else:
            db.session.add(User(username=username, password=generate_password_hash(password)))
            db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template("register.html")

#change password page to change password of an existing user
@app.route("/changepass",methods=["GET","POST"])
def changepass():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        newpassword = request.form.get("newpassword")
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password,password) or len(password) == 0 or len(newpassword) == 0:
            flash("Invalid username/password.")
            return render_template("changepass.html")
        else:
            user.password = generate_password_hash(newpassword)
            db.session.commit()
            return redirect(url_for('login'))
    else:
        return render_template("changepass.html")


#logout and return to login page
@app.route("/logout")
def logout():
    session.pop('username', None)
    data.user = ""
    return render_template("login.html")


#application page after login
@app.route("/concretile/")
def open_concretile():
    if 'username' in session:
        return render_template("concretile.html",data=data)
    else:
        return redirect(url_for('home'))

#upload function for all operations that involve uploading a file to the server
@app.route("/concretile/upload/",methods=['GET','POST'])
def upload():
    data.point_text = ""
    data.output_text = ""
    if request.method=="POST":
        match list(request.form.keys())[0]:
            case "upload_image":
                get_file('image_file',data.image_dir,["png","jpg","jpeg"])
            case "upload_grid":
                get_file('grid_file',data.image_dir,["png"])
            case "upload_mask":
                get_file('mask_file',data.image_dir,["png"])
            case "upload_model":
                get_model('config_file','path_file')
            case _:
                pass
        data.get_images()
        data.get_models()
        data.get_paths()
    return redirect(url_for('open_concretile'))

#update function for all operations that involve updating the displayed images or loaded model
@app.route("/concretile/update/",methods=['GET','POST'])
def update():
    data.point_text = ""
    data.output_text = ""
    if request.method=="POST":
        match request.form["action"]:
            case "update_image":
                data.update_image(request.form["image"])
            case "update_grid":
                data.update_grid(request.form["grid"])
            case "update_mask":
                data.update_mask(request.form["mask"])
            case "update_model":
                data.update_model(request.form["model"])
            case _:
                pass
    return redirect(url_for('open_concretile'))

#create function for all operations that involve creating a new image
@app.route("/concretile/create/",methods=['GET','POST'])
def create():
    data.point_text = ""
    data.output_text = ""
    if request.method=="POST":
        match request.form["action"]:
            case "create_mask":
                mask_name = request.form["mask_name"]
                mask_img = os.path.split(data.image_list[data.image_idx])[0]+"/mask/"+mask_name+".mask.png"
                data.model = concretile.load_model(data.static,data.config,data.pth)
                data.mask_img,data.output_text = concretile.segment_image(data.static,mask_img,data.img,data.model)
            case "create_grid":
                row_count = int(request.form["row_count"])
                col_count = int(request.form["col_count"])
                row_space = int(request.form["row_space"])
                col_space = int(request.form["col_space"])
                grid_x = int(request.form["grid_x"])
                grid_y = int(request.form["grid_y"])
                image = data.image_list[data.image_idx]
                if os.path.isfile(image):
                    with Image.open(image) as im:
                        grid_w,grid_l = im.size
                else:
                    grid_w = int(request.form["grid_w"])
                    grid_l = int(request.form["grid_l"])
                grid_name = request.form["grid_name"]
                grid_img = os.path.split(data.image_list[data.image_idx])[0]+"/grid/"+grid_name+".grid.png"
                data.grid_img,data.output_text = concretile.create_grid(data.static,grid_img,row_count,col_count,row_space,col_space,grid_w,grid_l,grid_x,grid_y)
            case "get_points":
                data.model = concretile.load_model(data.static,data.config,data.pth)
                data.points,data.output_text = concretile.get_points(data.static,data.img,data.grid_img,data.mask_img,data.model)
                data.point_classes = data.points.classes
                data.point_text, _ = data.points.save_points(data.static,"save")
            case _:
                pass
    return redirect(url_for('open_concretile'))

@app.route("/concretile/update/point",methods=['GET','POST'])
def update_point():
    if request.method=="POST":
        match request.form["action"]:
            case "update_point":
                pt_x = int(request.form["pt_x"])
                pt_y = int(request.form["pt_y"])
                pt_class = request.form["pt_class"]
                data.output_text = data.points.update_point(pt_x,pt_y,pt_class)
                data.point_text, _ = data.points.save_points(data.static,"save")
            case _:
                pass
    return redirect(url_for('open_concretile'))

@app.route("/concretile/save/points",methods=['GET','POST'])
def save_points():
    data.point_text, path = data.points.save_points(data.static,"save",True,50)
    data.output_text = f"Points have been saved to {path}."
    return redirect(url_for('open_concretile'))

@app.route("/concretile/clear/",methods=['GET','POST'])
def clear():
    data.clear()
    return redirect(url_for('open_concretile'))

@app.route("/concretile/upload/image/",methods=['GET','POST'])
def upload_image():
    return redirect(url_for('upload'))

@app.route("/concretile/upload/grid/",methods=['GET','POST'])
def upload_grid():
    return redirect(url_for('upload'))

@app.route("/concretile/upload/mask/",methods=['GET','POST'])
def upload_mask():
    return redirect(url_for('upload'))

@app.route("/concretile/upload/model/",methods=['GET','POST'])
def upload_model():
    return redirect(url_for('upload'))

@app.route("/concretile/update/image/",methods=['GET','POST'])
def update_image():
    return redirect(url_for('update'))

@app.route("/concretile/update/grid/",methods=['GET','POST'])
def update_grid():
    return redirect(url_for('update'))

@app.route("/concretile/update/mask/",methods=['GET','POST'])
def update_mask():
    return redirect(url_for('update'))

@app.route("/concretile/update/model/",methods=['GET','POST'])
def update_model():
    return redirect(url_for('update'))

@app.route("/concretile/create/grid/",methods=['GET','POST'])
def create_grid():
    return redirect(url_for('create'))

@app.route("/concretile/create/mask/",methods=['GET','POST'])
def create_mask():
    return redirect(url_for('create'))

@app.route("/concretile/create/points/",methods=['GET','POST'])
def create_points():
    return redirect(url_for('create'))

if __name__ == "__main__":
    app.run(debug=True)