This is an alternate implementation of the app that requires just the normal image (e.g.
the images in SoPIA_20221017/Concrete -- I assume these are the types of images that we 
will be getting from NIGS).

Also, right now, segmenting the image just loads a default image (see sample_segimg.png)
since we don't have a working model yet. The default image is just a ramdom, incomplete,
and probably a wrong segmentation of SoPIA_20221017/Aggregates/Project 2 Images/Amiterra
-112620/IMG_14488.png.

Ideally, the app should work as follows:
1. Load image to be segmented
    - This is put as the "Normal Image" in the radio buttons
2. Load the model (and whatever is needed with it)
3. Select "Normal Image" and segment it
    - The resulting image is put as the "Segmented Image" in the radio buttons
4. Select the "Segmented Image" and click "Create Grid"
    - A window will let you choose parameters of the grid. Click "Submit" and the grid
      will be displayed on the segmented image
5. Move the grid to your desired area and click "Confirm Grid"
    - The segmented image and the grid is combine and is put as the "Grid Image" in 
      the radio buttons
6. Click "Get Points" to get the cropped sections of the intersections from the normal
   image.
7. These cropped sections will be fed into a classification model (to be implemented)
   to get the results.
