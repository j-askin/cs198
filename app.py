from flask import Flask, render_template, Response, request, redirect, url_for
import sopia




app = Flask(__name__, template_folder='templates',static_folder='static')


@app.route("/")
@app.route("/sopia/")
def open_sopia():
    img, grid_img, seg_img = "", "", ""
    img_path = "data/test.jpg"
    grid_path = "data/grid.png"
    seg_path = "data/test_seg.jpg"
    seg_cfg, seg_pth, seg_mdl, = "", "", ""
    seg_cfg_path = "data/seg_test.py"
    seg_pth_path = "data/seg_test.pth"
    return render_template("sopia.html")

@app.route("/sopia/action/", methods=['GET','POST'])
def sopia_action():
    match request.form["action"]:
        case "load_image":
            img_path = request.form['image_path']
            img = sopia.load_image(img_path)
        case "load_mask":
            grid_path = request.form['grid_path']
            grid_img = sopia.load_grid(grid_path)
        case "load_grid":
            seg_path = request.form['seg_path']
            seg_img = sopia.load_seg(seg_path)
        case "load_model":
            seg_cfg_path = request.form['seg_cfg_path']
            seg_pth_path = request.form['seg_pth_path']
            seg_cfg, seg_pth, seg_mdl = sopia.load_model(seg_cfg_path,seg_pth_path)
        case "clear_data":
            img,grid_img,seg_img = "","",""
            seg_cfg, seg_pth, seg_mdl = "","",""
        case "create_mask":
            seg_img = sopia.segment_image(img,seg_mdl)
        case "create_grid":
            grid_path = request.form['grid_path']
            v_count = request.form['v_count']
            h_count = request.form['h_count']
            v_space = request.form['v_space']
            h_space = request.form['h_space']
            x_size = request.form['x_size']
            y_size = request.form['y_size']
            x_off = request.form['x_off']
            y_off = request.form['y_off']
            grid_img = sopia.create_grid(grid_path,v_count,v_space,h_count,h_space,x_size, x_off,y_size, y_off)
        case "get_points":
            pt_rad = request.form['pt_rad']
            pt_text = sopia.get_points(img,grid_img,seg_img,seg_mdl,pt_rad)

        case _:
            pass
    
    return render_template("sopia.html")


if __name__ == "__main__":
    img, grid_img, seg_img = "", "", ""
    img_path = "data/test.jpg"
    grid_path = "data/grid.png"
    seg_path = "data/test_seg.jpg"
    seg_cfg, seg_pth, seg_mdl, = "", "", ""
    seg_cfg_path = "data/seg_test.py"
    seg_pth_path = "data/seg_test.pth"
    app.run(debug=True)