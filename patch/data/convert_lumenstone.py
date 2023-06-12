from convert_mask import mask_convert

#palette taken from the configuration file, with added background color
palette = [
    [0, 0, 0], [255, 0, 0], [203, 255, 0], [0, 255, 102],
    [0, 101, 255], [204, 0, 255], [255, 76, 76], [219, 255, 76],
    [76, 255, 147], [76, 147, 255], [219, 76, 255], [255, 153, 153],
    [234, 255, 153],
]

mask_path = "lumenstone/masks"
out_path = "lumenstone/seg_colored"
mask_folders = ["test","train"]
out_folders = ["val","train"]
mode = "RGB"
mask_convert(palette=palette, mask_path=mask_path, out_path=out_path, mask_folders=mask_folders,out_folders=out_folders,mode=mode)

mask_path = "lumenstone/masks_human"
out_path = "lumenstone/seg_gray"
mask_folders = ["test","train"]
out_folders = ["val","train"]
mode = "L"
mask_convert(palette=palette, mask_path=mask_path, out_path=out_path, mask_folders=mask_folders,out_folders=out_folders,mode=mode)
