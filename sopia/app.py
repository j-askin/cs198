from flask import Flask, render_template, Response, request, redirect, url_for
import sopia


img, grid_img, seg_img = "", "", ""
img_path = "data/test.jpg"
grid_path = "data/grid.png"
seg_path = "data/test_seg.jpg"
seg_cfg, seg_pth, seg_mdl, = "", "", ""
seg_cfg_path = "data/seg_test.py"
seg_pth_path = "data/seg_test.pth"

app = Flask(__name__)


@app.route("/")
@app.route("/sopia/")
def open_sopia():
    return render_template("sopia.html")

@app.route("/sopia/load_image/", methods=['POST'])
@app.route("/sopia/load_image/<img_path>", methods=['POST'])
def load_image(img_path="None"):
    print(f"Image path: {img_path}")
    img = sopia.load_image(img_path)
    print(f"Image: {img}")

@app.route("/sopia/load_grid/", methods=['POST'])
@app.route("/sopia/load_grid/<grid_path>", methods=['POST'])
def load_grid(grid_path="None"):
    print(f"Grid path: {grid_path}")
    grid_img = sopia.load_grid(grid_path)
    print(f"Grid: {grid_img}")


@app.route("/sopia/load_mask/", methods=['POST'])
@app.route("/sopia/load_mask/<seg_path>", methods=['POST'])
def load_seg(seg_path=""):
    print(f"Segmented mask path: {seg_path}")
    seg_img = sopia.load_seg(seg_path)
    print(f"Segmented mask: {seg_img}")

@app.route("/sopia/clear_data/", methods=['POST'])
def clear_data():
    img,grid_img,seg_img = "","",""
    seg_cfg, seg_pth, seg_mdl = "","",""
    print("Images and model cleared.")


@app.route("/sopia/load_model/", methods=['POST'])
@app.route("/sopia/load_model/<seg_cfg_path>/<seg_pth_path>", methods=['POST'])
def load_model(seg_cfg_path = "",seg_pth_path = ""):
    print(f"Segmenter config path: {seg_cfg_path}")
    print(f"Segmenter paths path: {seg_pth_path}")
    seg_cfg, seg_pth, seg_mdl = sopia.load_model(seg_cfg_path,seg_pth_path)
    print(f"Segmenter config: {seg_cfg}")
    print(f"Segmenter paths: {seg_pth}")
    if seg_mdl not in ["",None]:
         print("Successfully loaded segmenter model.")

@app.route("/sopia/create_mask/", methods=['POST'])
@app.route("/sopia/create_mask/<img>/<seg_mdl>", methods=['POST'])
def segment_image(img = "", seg_mdl = ""):
    print(f"Image: {img}")
    if seg_mdl not in ["",None]:
         print("Segmenter model exists")
    seg_img = sopia.segment_image(img,seg_mdl)
    print(f"Segmented mask: {seg_img}")


@app.route("/sopia/classify_point/", methods=['POST'])
@app.route("/sopia/classify_point/<color>/<seg_mdl>", methods=['POST'])
def classify_point(color = (0,0,0), seg_mdl = ""):
    print(f"Color: {tuple(color)}")
    if seg_mdl not in ["",None]:
         print("Segmenter model exists")
    result = sopia.classify_point(color,seg_mdl)
    print(f"Class: {result}")

@app.route("/sopia/create_grid/", methods=['POST'])
@app.route("/sopia/create_grid/<grid_path>", methods=['POST'])
def create_grid(out_path = "grid.png", v_count = 10,v_space = 200,h_count = 10,h_space = 200,x_size = 3396, x_off = 100, y_size = 2547, y_off = 100):
    print(f"Grid dimensions: ({h_count} x {v_count})")
    print(f"Grid spacing: ({h_space} x {v_space})")
    print(f"Grid size: ({x_size} x {y_size})")
    print(f"Grid size: ({x_size} x {y_size})")
    print(f"Grid position: ({x_off} x {y_off})")
    print(f"Grid path: {out_path}")
    grid_img = sopia.create_grid(out_path,v_count,v_space,h_count,h_space,x_size, x_off,y_size, y_off)
    print(f"Grid: {grid_img}")

@app.route("/sopia/get_points/", methods=['POST'])
@app.route("/sopia/get_points/<grid_path>", methods=['POST'])
def get_points(img="",grid_img="",seg_img="",seg_mdl="",pt_rad=25):
    print(f"Image: {img}")
    print(f"Grid: {grid_img}")
    print(f"Segmented maskh: {seg_img}")
    if seg_mdl not in ["",None]:
        print("Segmenter model exists")
    print(f"Point radius: {pt_rad}")
    pt_text = sopia.get_points(img,grid_img,seg_img,seg_mdl,pt_rad)

