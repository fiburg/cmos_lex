# import the necessary packages
import numpy as np
import argparse
import glob
import cv2
from scipy import ndimage
import matplotlib.pyplot as plt
import cmos

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged

sky_imager = cmos.SkyImager("hq")
files = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/*_1132*.jpg"
# loop over the images
for imagePath in sorted(glob.glob(files)):
    # load the image, convert it to grayscale, and blur it slightly

    sky_imager.load_image(imagePath,1000)
    image = sky_imager.original_image.copy()
    print("COLORS ", image[1000, 1000, :])
    # image[np.where(image[:,:,0] <1)] = 73
    # image[np.where(image[:, :, 1] < 1)] = 83
    # image[np.where(image[:, :, 2] < 1)] = 118
    image = cv2.resize(image,None,fx=0.3, fy=0.3, interpolation = cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)



    # apply Canny edge detection using a wide threshold, tight
    # threshold, and automatically determined threshold
    wide = cv2.Canny(blurred, 10, 200)
    tight = cv2.Canny(blurred, 30, 210)
    auto = auto_canny(blurred)

    auto_dilated = ndimage.binary_dilation(auto).astype(int)
    fill_clouds_auto = ndimage.binary_fill_holes(auto_dilated).astype(int)

    wide_dilated = ndimage.binary_dilation(wide)
    fill_clouds_wide = ndimage.binary_fill_holes(wide_dilated).astype(int)

    tight_dilated = ndimage.binary_dilation(tight)
    fill_clouds_tight = ndimage.binary_fill_holes(tight_dilated).astype(int)

    # show the images
    # cv2.imshow("Original", sky_imager.image)
    cv2.imshow("Edges", np.hstack([wide, tight, auto]))

    fig, (ax1,ax2,ax3,ax4) = plt.subplots(ncols=4)
    ax3.imshow(fill_clouds_auto)
    ax3.set_title("Auto_edges")
    ax1.set_title("Wide edges")
    ax1.imshow(fill_clouds_wide)
    ax2.set_title("Tight edges")
    ax2.imshow(fill_clouds_tight)

    ax4.imshow(image)
    plt.show()

    cv2.waitKey(0)