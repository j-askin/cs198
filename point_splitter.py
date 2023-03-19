'''
This program splits an input image into "bubble" images of a defined pixel radius.
Training pattern is "grid" - get overlapping bubbles arranged in a grid for maximum coverage
Testing pattern is "random" - get bubbles at random coordinates
Note: jpg results in square images, png results in circular images
'''
import os, cv2, random, time
import numpy as np
#from tkinter import filedialog

def get_bubble(img_path="test.jpg",dest_path = f"save/{time.strftime('%m%y%d-%H%M%S',time.localtime(time.time()))}", pt_rad = 250, randomize=False, samples = 10):
    #generate output directory
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    #generate blank mask
    blank_mask = np.zeros((pt_rad*2,pt_rad*2,3), np.uint8)
    cv2.circle(blank_mask, (pt_rad,pt_rad),pt_rad,(255,255,255),thickness = -1)
    #load images
    cv_img = cv2.imread(img_path)
    #cov_img = np.array(cv_img)
    #cir_img = np.array(cv_img)
    img_y,img_x = cv_img.shape[0],cv_img.shape[1]
    y_l, x_l = ((img_y%pt_rad)/2),((img_x%pt_rad)/2)#get padding along edges
    y_l, y_u, x_l, x_u = int(y_l), int(img_y-y_l), int(x_l), int(img_x-x_l)#set boundaries, temp
    points_x, points_y = [],[]
    if randomize:
        for i in range(samples):
            point_x = random.randint(pt_rad,img_x-pt_rad)
            point_y = random.randint(pt_rad,img_y-pt_rad)
            r1,r2,r3,r4 =(point_x-pt_rad),(point_x+pt_rad),(point_y-pt_rad),(point_y+pt_rad)
            temp = cv2.cvtColor(cv_img[r3:r4,r1:r2], cv2.COLOR_BGR2BGRA)
            temp[:,:,3] = blank_mask[:,:,0]
            cv2.imwrite(os.path.join(dest_path,f"{os.path.split(img_path)[1].split('.')[0]}_({i})_{r2-r1}x{r4-r3}.jpg"),temp)
            #cv2.circle(cov_img, (point_x,point_y),pt_rad,(0,255,0),thickness = -pt_rad)
            #cv2.circle(cir_img, (point_x,point_y),pt_rad,(0,0,255),thickness = 1)
        #cv2.imwrite(os.path.join(dest_path,"coveredoutput.png"),cov_img)
        #cv2.imwrite(os.path.join(dest_path,"circleoutput.png"),cir_img)
    else:
        points_x = [xp for xp in range(x_l+pt_rad,x_u,pt_rad)]
        points_y = [yp for yp in range(y_l+pt_rad,y_u,pt_rad)]
        for x in range(len(points_x)):
            for y in range(len(points_y)):
                r1,r2,r3,r4 =(points_x[x]-pt_rad),(points_x[x]+pt_rad),(points_y[y]-pt_rad),(points_y[y]+pt_rad)
                temp = cv2.cvtColor(cv_img[r3:r4,r1:r2], cv2.COLOR_BGR2BGRA)
                temp[:,:,3] = blank_mask[:,:,0]
                cv2.imwrite(os.path.join(dest_path,f"{os.path.split(img_path)[1].split('.')[0]}_({x},{y})_{r2-r1}x{r4-r3}.jpg"),temp)
                #cv2.circle(cov_img, (points_x[x],points_y[y]),pt_rad,(0,255,0),thickness = -pt_rad)
                #cv2.circle(cir_img, (points_x[x],points_y[y]),pt_rad,(0,0,255),thickness = 1)
        #cv2.imwrite(os.path.join(dest_path,"coveredoutput.png"),cov_img)
        #cv2.imwrite(os.path.join(dest_path,"circleoutput.png"),cir_img)
    print(f"Points written to {dest_path}.")


def main():
    #data_path = filedialog.askdirectory()
    #data_path = os.path.join(os.path.expanduser("~"),f"Desktop/bubblesplitter/data")
    #dest_path = os.path.join(os.path.expanduser("~"),f"Desktop/bubblesplitter/save/{time.strftime('%m%y%d-%H%M%S',time.localtime(time.time()))}")
    data_path = os.path.join(os.path.split(os.path.abspath(__file__))[0],"data") #place dataset in "data" folder in the same directory as this file
    dest_path = os.path.join(os.path.split(os.path.abspath(__file__))[0],f"save/{time.strftime('%m%y%d-%H%M%S',time.localtime(time.time()))}")
    print(os.listdir(data_path))
    for data_class in os.listdir(data_path):
        print(data_class)
        data_class_path = os.path.join(data_path,data_class)
        if os.path.isdir(os.path.join(data_path,data_class)):
            for data_img in os.listdir(data_class_path):
                data_img_path = os.path.join(data_class_path,data_img)
                if os.path.isfile(data_img_path):
                    dest_img_train_path = os.path.join(dest_path,os.path.join("train",data_class))
                    get_bubble(data_img_path,dest_img_train_path,randomize=False)
                    dest_img_test_path = os.path.join(dest_path,os.path.join("test",data_class))
                    get_bubble(data_img_path,dest_img_test_path,randomize=True,samples=10)
                    dest_img_test_path = os.path.join(dest_path,os.path.join("val",data_class))
                    get_bubble(data_img_path,dest_img_test_path,randomize=True,samples=10)

if __name__ == "__main__":
    main()