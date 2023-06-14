About Concretile
================

Concretile is a web application designed to partially automate the process of point counting on concrete thin-section samples, with a focus on samples taken in the Philippines. This manual will guide you in installing and using the application, as well as in training models used for the application's image segmentation functions.
To run the application locally, use the ***run_local.sh*** file in the root directory of the application. This will run the application as a local debug application that will not be visible to other computers. Alternatively, you can use the ***run_remote.sh*** file in the root directory of the application and run the application as a remote server. In both cases, you can access the application from the same computer by opening your browser and entering the url: ***<http://localhost:5000>*** in the address bar.

Directory structure
-------------------

```bash

cs198
│   linux-fix_mmsegmenation.sh
│   linux-install.sh
│   linux-install_gpu-cu117.sh
│   linux-install_gpu-cu118.sh
│   linux-install_gpu-rocm542.sh
│   linux-run-remote.sh
│   linux-run_local.sh
│   linux-train_model.sh
│   README.md
│   windows-fix_mmsegmenation.sh
│   windows-install.sh
│   windows-install_gpu-cu117.sh
│   windows-install_gpu-cu118.sh
│   windows-run_local.sh
│   windows-run_remote.sh
│   windows-train_model.sh
│
├───mmsegmentation
│   ├───configs
│   │   ├───custom
│   │   │
│   │   └───_base_
│   │       └───datasets
│   │
│   ├───data
│   │
│   ├───mmseg
│   │   └───datasets
│   │
│   └───work_dirs
│
├───patch
│   ├───configs
│   │   ├───custom
│   │   │       fastfcn_r50-d32_jpu_psp_4xb4-80k_lumenstone-600x800.py
│   │   │       fastfcn_r50-d32_jpu_psp_4xb4-80k_sopia-600x800.py
│   │   │       upernet_r50_4xb4-80k_lumenstone-600x800.py
│   │   │       ...
│   │   │
│   │   └───_base_
│   │       └───datasets
│   │               lumenstone_dataset.py
│   │               sopia_dataset.py
│   │
│   ├───data
│   │       augment_dataset.py
│   │       augment_lumenstone.py
│   │       augment_sopia.py
│   │       augment_sopia_xpl.py
│   │       convert_lumenstone.py
│   │       convert_mask.py
│   │       convert_sopia.py
│   │       convert_sopia_xpl.py
│   │       generate_sopia_xpl.py
│   │
│   └───mmseg
│       └───datasets
│               lumenstone.py
│               sopia.py
│               __init__.py
│
├───Sample Data
│   │   INFO.txt
│   │
│   └───lumenstone
│       ├───raw
│       │   ├───train
│       │   │       01.jpg
│       │   │       02.jpg
│       │   │       ...
│       │   │
│       │   └───val
│       │           01.jpg
│       │           02.jpg
│       │           ...
│       │
│       └───seg
│           ├───train
│           │       01.png
│           │       02.png
│           │       ...
│           │
│           └───val
│                   01.png
│                   02.png
│                   ...
│
└───src
    │   app.py
    │   concretile.py
    │
    ├───static
    │   │   scripts.js
    │   │   styles.css
    │   │
    │   ├───images
    │   │   └───uploads
    │   │       │   10.jpg
    │   │       │
    │   │       ├───grid
    │   │       │       example_grid.grid.png
    │   │       │
    │   │       └───mask
    │   │               10.mask.png
    │   │               gen_10.mask.png
    │   │
    │   ├───models
    │   │   └───lumenstone_fastfcn
    │   │           lumenstone_fastfcn.pth
    │   │           lumenstone_fastfcn.py
    │   │
    │   └───save
    └───templates
            changepass.html
            concretile.html
            login.html
            register.html
```

Installation Instructions
-------------------------

1. Install Python 3.11 on your computer using the instructions from ***<https://www.python.org/>*** for your system.
2. Install Git using the instructions from ***<https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>*** for your system. While this step is recommended to download Concretile, it is not required.
3. Download the application from this github repository: ***<https://github.com/j-askin/cs198>*** by using the command ***git clone <https://github.com/j-askin/cs198> -o Concretile*** or opening the link in a browser, clicking on the ***Code*** button and selecting ***Download ZIP*** to download the source code as a ZIP file. In this case, extract the contents of the ZIP file to the projects folder.
4. Run the ***windows-install.sh*** or the ***linux-install.sh*** file depending on your operating system to install all required packages and dependencies. Be sure to have around 3GB of free space beforehand.
5. If you have an NVIDIA GPU installed, you can instead run ***windows-install_gpu-[VERSION].sh*** or ***linux-install_gpu-[VERSION].sh*** instead to enable support for GPU acceleration, where [VERSION] refers to the CUDA version installed on your computer. You can check this using either the ***nvidia-smi*** command or the ***nvcc --version*** command in the terminal. If you do not have CUDA installed, you can install it using the instructions at ***<https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html>***. GPU support is highly recommended due to the significant amount of time it takes to train a model.
6. Open the ***run_local.sh*** file corresponding to your operating system to run Concretile as a local application. Otherwise, run the ***run_remote.sh*** command to allow other computers to access the web application if they are on the same network as your computer.


Using the Application
---------------------

1. Run the ***run_local.sh*** or ***run_remote.sh*** file corresponding to your operating system. Then, open a web browser and type ***<http://localhost:5000>*** on the address bar.
2. Alternatively, you can access the application running on a different computer by typing ***<http://[HOST_ADDRESS]:5000>*** instead, replacing ***[HOST_ADDRESS]*** with the IP address of the computer running the application. You can use a website like ***<https://ifconfig.me/>*** or command line tools like ***ipconfig*** for Windows and ***ifconfig*** for Linux to find the IP address of your computer.
3. Register a new account for the application using the ***Register*** button, then login using your new credentials. You can also change your password in the login screen using the ***Change Password*** button.
4. Upload an image using the ***Image*** field to select an image and confirm using the ***Upload Image*** button to the right of the field. You can this step if you have already uploaded an image.
5. Do the same for the ***Config*** and ***Weights*** field to upload a model generated in MMSegmentation. Remember that the ***.py*** file goes to the ***Config*** field and the ***.pth*** file goes to the ***Weights*** field. You can also skip this step if you already have a model uploaded.
6. Select an image and model using the dropdown menus beside the ***Update Image*** and ***Update Model*** buttons, then confirming with the buttons. The currently selected image and model is shown at the right of the app. The selected image is visible in the image window at the upper-left of the app.
7. Create a new grid by entering the appropriate parameters in the input fields above the ***Create Grid*** button, then clicking on the ***Create Grid*** button. Note that all of the fields except the ***Grid Name*** field take non-negative integers as input.
8. Generate a segmentation mask using the ***Segment Image*** button. Be sure to fill up the ***Mask Name*** field with the filename of the generated segmentation mask first.
9. Select a grid and segmentation mask using the ***Update Grid*** and ***Update Mask*** buttons respectively. You can also select another segmentation mask with ***Update Mask 2***, which will only be used for the ***Compare Model Points*** function. The grid and masks are also shown in the image window. If you want to show or hide the image, grid, or masks, click on the corresponding checkboxes at the bottom of the app.
10. Click on ***Get Grid Points*** to get the grid points for the selected image, grid, and segmentation mask. This also requires a loaded model. Be sure that you selected the correct segmentation mask in ***Update Mask*** and not in ***Update Mask 2***.
11. Review the points displayed in the output text window on the right of the app, as well as the ***Tile Map*** overlaid on the image view. You can use the fields and dropdown for the ***Update Point Class*** to manually change the classes of individual points.
12. If you are satisfied with the results of the point counting, click on ***Save Point Classes*** to save the result of the point counting to a text file and a set of images in the ***save*** folder.
13. If you want to compare the points extracted from two different masks, such as a model-generated mask and a manually annotated ground truth mask, you can load the masks in ***Update Mask*** and ***Update Mask 2*** respectively, the click on ***Compare Model Points*** to get a report of the accuracy and differences between the two masks.
14. If you have difficulties in viewing details of the image, you can use the ***Zoom Level*** slider to enlarge the image window and all images and masks being displayed, and drag the image window to view different parts of the image.
15. If there are issues in displaying the image or using any of the functions, try reselecting the images, masks, and model. You can verify that these are properly loaded in the labels to the right of the app.

Training a Model
----------------

1. Acquire a dataset of concrete sample images. Each image in the dataset must have annotations as a separate (but similarly named) mask image with different colors corresponding to different classes of material. Refer to the sample dataset in ***Sample Data*** for an example.
2. Separate the images and masks dataset into two folders. Afterwards, separate each folder into two groups, one containing training images and another containing evaluation images. The images and masks in each subfolder must match. Refer to the sample dataset in ***Sample Data*** for an example.
3. Copy the dataset into the ***data*** folder of MMSegmentation or the ***data*** folder in the ***patch*** folder.
4. If you want to train a model with a new configuration, make a new configuration file in the ***configs*** folder in the MMSegmentation directory. Due to the various considerartions and options involved in making a configuration, you are advised to refer to the documentation in ***<https://mmsegmentation.readthedocs.io/en/latest/>*** for more information, or use the other configurations in the ***configs*** folder for reference. Place your configuration in the ***custom*** subfolder of either the ***mmsegmentation*** directory or the ***patch*** folder when it is done.
5. Run the ***fix_mmsegmentation.sh*** shell file corresponding to your operating system. This is to ensure that any additional or modified files that were added did not break the installed MMSegmentation package.
6. Open a terminal and navigate to the project directory.
7. Run the command ***nohup bash tools/dist_train.sh mmsegmentation/configs/custom/[CONFIGURATION_NAME].py 1 > training.log 2>&1 &***, replacing ***[CONFIGURATION_NAME]*** with the name of the configuration file you want to use. This command will run the training procedure in the background and save the training log in the ***training.log*** file (you can use any name for this file) for later reference.
8. If you intend to train on either of the two ***Sample Data*** datasets or modifications thereof using one of the existing training configurations and you have little experience with the terminal, you can skip steps 4, 6, and 7 and instead edit and run the ***train-model.sh*** shell script corresponding to your operating system instead. Simply replace the ***[CONFIGURATION_NAME]*** portion with the name of the configuration file you wish to use for training.
9. Wait for the training to finish. Training can take several days to complete depending on your hardware and whether you have a GPU installed. Make sure that your computer is running during the training process.
10. There is a high chance that your training process will suddenly fail in the first few minutes due to a lack of resources. Make sure that no other applications using the GPU such as games or editing software are running during the training process. You can check if your training process is still running using the ***nvidia-smi*** command in the terminal or by using your task manager if you are on Windows. A high GPU usage is a sign that your training process is still running.
11. Once training is finished, you can retreive your model in the ***work_dirs*** folder in the MMSegmentation directory. The files you are looking for are in a folder with the same name as the configuration file you used and are a configuration file that ends in ***.py*** (this file is a more comprehensive version of the file you used in training) and a paths file named ***iter_[ITERATIONS].pth***, where [ITERATIONS] is the number of iterations that the model was trained on. Use the highest number of iterations for better accuracy.
