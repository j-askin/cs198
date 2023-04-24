import sopia


static = "C:/Users/Migui/Desktop/cs198-new/cs198/static"
config = "models/mask_test/mask_test.py"
pth = "models/mask_test/mask_test.pth"
model = sopia.load_model(static,config,pth)
image = "images/test/test.png"
mask_img,output_text = sopia.segment_image(static,image,model)
print(output_text)