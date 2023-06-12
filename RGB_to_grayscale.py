import glob
import os
import os.path

import numpy as np
from PIL import Image

p = {                       # palette of the dataset being used
    "[0 0 0]": 0,
    "[31 120 180]": 1,
    "[106 61 154]": 2,
    "[33 170 157]": 3,
    "[227 26 28]": 4,
    "[177 89 40]": 5,
    "[85 24 183]": 6,
    "[35 60 178]": 7,
    "[16 143 155]": 8,
    "[95 13 159]": 9,
    "[106 176 25]": 10,
    "[168 32 34]": 11,
    "[29 13 169]": 12,
    "[220 17 99]": 13,
    "[255 244 116]": 14
}

def main():
    path = "C:/Users/josh/Desktop/masks/"        # path/to/masks/folder
    modes = [path + "Aggregates", path + "Cement"]    # subfolders in the masks folder
    src_path_list = []
    for mode in modes:
        src_path_list.extend(glob.glob(os.path.join(mode, '*.png')))
    x = len(src_path_list)
    for a in range(x):
        img = np.array(Image.open(src_path_list[a]))
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                img[i][j] = p[f"[{int(img[i][j][0])} {int(img[i][j][1])} {int(img[i][j][2])}]"]
        img = Image.fromarray(img)
        img = img.convert("L")
        img.save(src_path_list[a])
        print(f"{a+1} of {x} done.")
    print()
    print('Done!')

if __name__ == '__main__':
    main()