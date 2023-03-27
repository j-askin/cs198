from sopia import load_image,load_grid,load_seg,load_model,segment_image,create_grid,classify_point,get_points



img, grid_img, seg_img = "", "", ""
img_path = "data/test.jpg"
grid_path = "data/grid.png"
seg_path = "data/test_seg.png"


seg_cfg, seg_pth, seg_mdl, = "", "", ""
seg_cfg_path = "data/seg_test.py"
seg_pth_path = "data/seg_test.pth"

#CLI interface for testing
while True:
    select = input('''Select an option:\n\
    0. Exit the program\n\
    1. Load an image\n\
    2. Load a grid overlay\n\
    3. Load a segmented image\n\
    4. Clear loaded images and models\n\
    5. Load a segmenter model\n\
    6. Generate a segmented image\n\
    7. Generate a grid overlay\n\
    8. Get points for point counting\n\
    ''')
    match int(select):
        case 0:
            break
        case 1:
            img = load_image(img_path)
        case 2:
            grid_img = load_grid(grid_path)
        case 3:
            seg_img = load_seg(seg_path)
        case 4:
            img,grid_img,seg_img = "","",""
            seg_cfg, seg_pth, seg_mdl = "","",""
        case 5:
            seg_cfg, seg_pth, seg_mdl = load_model(seg_cfg_path,seg_pth_path)
        case 6:
            out_path = input("Input the name of the segmented mask image (leave blank for default)")
            seg_img = segment_image(img,seg_mdl,out_path)
        case 7:
            try:
                out_path = input("Input the name of the grid image.")
                v_count = int(input("Enter the number of rows to count."))
                v_space = int(input("Enter the amount of space between rows (in px)."))
                h_count = int(input("Enter the number of columns to count."))
                h_space = int(input("Enter the amount of space between columns (in px)."))
                x_size = int(input("Enter the expected width of your input (in px)."))
                x_off = int(input("Enter the distance of the first column from the left side of the image."))
                y_size = int(input("Enter the expected height of your input (in px)."))
                y_off = int(input("Enter the distance of the first row from the top side of the image."))
                grid_img = create_grid(out_path,v_count,v_space,h_count,h_space,x_size, x_off,y_size, y_off)
            except Exception as e:
                print(f"Invalid input: {e}")
        case 8:
            pt_rad = int(input("Enter the radius of each point to extract."))
            pt_text = get_points(img,grid_img,seg_img,seg_mdl,pt_rad)
        case _:
            print("Invalid option input.")