from sopia import *



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

#CLI interface for testing
while True:
    select = input('''Select an option:\n\
    0. Exit the program\n\
    1. Load an image\n\
    2. Load a grid overlay\n\
    3. Load a segmented image\n\
    4. Clear loaded images\n\
    5. Load a segmenter model\n\
    6. Load a classifier model\n\
    7. Generate a segmented image\n\
    8. Classify the current image\n\
    9. Generate a grid overlay\n\
    10. Get points for point counting (circle)\n\
    11. Get points for point counting (point)\n\
    ''')
    match int(select):
        case 0:
            break
        case 1:
            img,grid_img,seg_img = load_images(img_path,grid_path,seg_path)
        case 2:
            grid_img = load_grid(grid_path)
        case 3:
            seg_img = load_seg(seg_path)
        case 4:
            img,grid_img,seg_img = clear_load()
        case 5:
            seg_cfg, seg_pth, seg_lbl, seg_mdl = load_seg_model(seg_cfg_path,seg_pth_path,seg_lbl_path)
        case 6:
            cls_cfg, cls_pth, cls_mdl = load_cls_model(cls_cfg_path,cls_pth_path)
        case 7:
            seg_img = segment_image(img,seg_mdl)
        case 8:
            result = classify_image(img,cls_mdl)
        case 9:
            try:
                grid_path = input("Input the name of the grid image.")
                v_count = int(input("Enter the number of rows to count."))
                v_space = int(input("Enter the amount of space between rows (in px)."))
                h_count = int(input("Enter the number of columns to count."))
                h_space = int(input("Enter the amount of space between columns (in px)."))
                x_size = int(input("Enter the expected width of your input (in px)."))
                x_off = int(input("Enter the distance of the first column from the left side of the image."))
                y_size = int(input("Enter the expected height of your input (in px)."))
                y_off = int(input("Enter the distance of the first row from the top side of the image."))
                grid_img = create_grid(grid_path,v_count,v_space,h_count,h_space,x_size, x_off,y_size, y_off)
            except Exception as e:
                print(f"Invalid input: {e}")
        case 10:
            pt_rad = int(input("Enter the radius of each point to extract."))
            pt_text = get_points(img,grid_img,seg_img,pt_rad,cls_mdl)
        case 11:
            pt_text = get_points(img,grid_img,seg_img,1,cls_mdl)
        case _:
            print("Invalid option input.")