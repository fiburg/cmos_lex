import cmos
import matplotlib.pyplot as plt
from scipy.ndimage import label
import numpy as np
import glob
from scipy import ndimage
from skimage import feature
import cv2

# file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180829/LEX_WKM2_Image_20180901_092840_UTCp1.jpg"
file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_091040_UTCp1.jpg"

# file = "W:/Aufzeichnung/wkm2/jpg/LEX_WKM2_Image_20180901_094820_UTCp1.jpg"

# files = "W:/Aufzeichnung/wkm2/jpg/LEX_WKM2_Image_*_UTCp1.jpg"
# file = sorted(glob.glob(files))[-1]

sky_imager = cmos.SkyImager("hq")
sky_imager.load_image(file,cloud_height=540)


sky_imager.shadow_on_cam_position()

sky_imager.create_lat_lon_array()
sky_imager.create_lat_lon_cloud_mask()
sky_imager_setup = cmos.SkyImagerSetup("hq")


def auto_canny(image, sigma=0.01):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    # compute the median of the single channel pixel intensities
    v = np.median(blurred)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, 10, 250)

    # return the edged image
    return edged

_ = sky_imager.create_cloud_mask_canny_edges(0,0,1)
edges = feature.canny(sky_imager.grey_scale_image,sigma=1)
edged = auto_canny(sky_imager.image)
hist = np.histogram(sky_imager.grey_scale_image, bins=np.arange(1, 256 ))
fill_clouds = ndimage.binary_fill_holes(edges)


fig,(ax1,ax2,ax3) = plt.subplots(ncols=3)
ax1.plot(hist[1][:-1], hist[0], lw=2)
ax1.set_title('histogram of gray values')
ax2.imshow(edged, cmap="gray")
ax3.imshow(sky_imager.image)
plt.show()

# for sigma in range(10):
#     fig, axes = plt.subplots(ncols=20, nrows=2,sharex=True,sharey=True)
#
#
#     for i,_ in enumerate(axes[:,0]):
#         for j, _ in enumerate(axes[0,:]):
#             for tick in axes[i,j].xaxis.get_major_ticks():
#                 tick.label.set_fontsize(1)
#
#             for tick in axes[i,j].yaxis.get_major_ticks():
#                 tick.label.set_fontsize(1)
#
#             print("i=%i, j=%i"%(i,j))
#             low = i
#             heigh = j
#             cloud_mask = sky_imager.create_cloud_mask_canny_edges(low,heigh,sigma=sigma)
#             axes[i,j].imshow(cloud_mask)
#             axes[i,j].set_title("Low=%5.3f Heigh=%5.3f"%(low,heigh), fontsize=3)
#     plt.tight_layout()
#     plt.savefig("canny_edges_sigma_%i.pdf"%sigma)
#     print("Sigma %i finished"%sigma)

