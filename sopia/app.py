from sopia import load_images,load_img,load_grid,load_seg,clear_load
from sopia import load_seg_model,load_cls_model,segment_image,classify_image,create_grid,get_points
from flask import Flask, render_template, Response, request, redirect, url_for



img, grid_img, seg_img = "", "", ""
img_path = "data/test.jpg"
grid_path = "data/grid.png"
seg_path = "data/test_seg.jpg"


seg_cfg, seg_pth, seg_lbl, seg_mdl, = "", "", "", ""
seg_cfg_path = "data/seg_test.py"
seg_pth_path = "data/seg_test.pth"
seg_lbl_path = "data/seg_label.json"

cls_cfg, cls_pth, cls_mdl = "", "", ""
cls_cfg_path = "data/cls_test.py"
cls_pth_path = "data/cls_test.pth"
result = {"pred_class":"","pred_label":"","pred_score":0}

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, Flask!"


@app.route("/sopia/")
@app.route("/sopia/<image>")
def open_sopia(image=None):
    return render_template("sopia.html",image=image)

@app.route("/sopia/load_image/<img_path>", methods=['POST'])
def load_image(img_path="data/test.jpg"):
    #Moving forward code
    img = load_img(img_path)
    return render_template('index.html', output_display=f"Loaded image{img}")
