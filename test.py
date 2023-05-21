import sopia

#Test Script used to test the functionality of the library

#sopia.create_grid("C:/Users/Migui/Desktop/cs198/static/images/uploads","grid.png",10,10,120,120,1920,1200,460,80)
#Paths to files and directories
static = "C:/Users/Migui/Desktop/cs198/static/"
image_path = "images/uploads/SOPIA_RAW_001_IMG001_PPL_raw.png"
grid_path = "images/uploads/grid.png"
mask_path = "images/uploads/SOPIA_RAW_001_IMG001_PPL.png"
config_path = "models/sopia/sopia.py"
pth_path = "models/sopia/sopia.pth"
save_path = "save/"


#Test the point counting function
print(sopia.verify_file(static,image_path))
model = sopia.load_model(static,config_path,pth_path)
print("Model loaded")
print(model.dataset_meta)
print("Model classes")
print(model.dataset_meta["classes"])
print("Model palette")
print(model.dataset_meta["palette"])

mask_img,output_text = sopia.segment_image(static,image_path,model)
print("Mask generated")
print(output_text)
points, msg = sopia.get_points(static,image_path,grid_path,mask_path,model,save_path)
print("Points generated")
print(msg)
msg = points.save_points(static,save_path,True,25)
print("Points saved.")
print(msg)