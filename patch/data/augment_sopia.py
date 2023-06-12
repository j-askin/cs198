from augment_dataset import augment_directory

#Dataset-specific settings for augmentation
data_dir="sopia" #original data directory
out_dir="sopia_augmented" #output data directory
#All image-mask pairs are assumed to have the same filename up to an extension label.
raw_train_ext = ".png" #extension for raw training image
raw_val_ext = ".png" #extension for raw evaluation image
mask_train_ext = ".png" #extension for training mask image
mask_val_ext = ".png" #extension for evaluation mask image
train_count = 5 #number of additional training images  to generate per training image
val_count = 5 #number of additional evaluation images to generate per evaluation image
augment_directory(data_dir = data_dir, out_dir = out_dir, train_count = train_count, val_count = val_count, raw_train_ext = raw_train_ext, raw_val_ext = raw_val_ext, mask_train_ext = mask_train_ext, mask_val_ext = mask_val_ext)