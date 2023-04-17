

def get_images(self):
    self.image_list = [""]
    self.image_dir = os.path.join(self.root_dir,self.image_dir)
    if not os.path.exists(self.image_dir):
        os.mkdir(self.image_dir)
    for dir in os.listdir(self.image_dir):
        if os.path.isdir(dir):
            print(dir)