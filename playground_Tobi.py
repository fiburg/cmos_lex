import cmos
import matplotlib.pyplot as plt
from scipy.ndimage import label
import numpy as np
import glob

# file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180829/LEX_WKM2_Image_20180901_092840_UTCp1.jpg"
file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_112340_UTCp1.jpg"

# file = "W:/Aufzeichnung/wkm2/jpg/LEX_WKM2_Image_20180901_094820_UTCp1.jpg"

# files = "W:/Aufzeichnung/wkm2/jpg/LEX_WKM2_Image_*_UTCp1.jpg"
# file = sorted(glob.glob(files))[-1]

sky_imager = cmos.SkyImager("hq")
sky_imager.load_image(file,cloud_height=540)

print(sky_imager.date)
print(sky_imager.height)
print(sky_imager.sun_elevation,sky_imager.sun_azimuth)

sky_imager.shadow_on_cam_position()
sky_imager._rotate_image(45)
rotated = sky_imager.rotated

# cloud_mask = sky_imager.create_cloud_mask_canny_edges()

# sky_imager.sun_position_in_image()

sky_imager.create_lat_lon_array()
sky_imager.create_lat_lon_cloud_mask()

sky_imager_setup = cmos.SkyImagerSetup("hq")
sun_pos_img = sky_imager_setup.find_sun(file)
print("Sun pos in image:", sun_pos_img)
print("Sun pos theo:", sky_imager.sun_azimuth, sky_imager.sun_elevation)

# print(sky_imager.angle_array)

# sky_imager.hemisphere_to_plain(cbh=1000)

fig, (ax1,ax2, ax3) = plt.subplots(ncols=3)
ax1.imshow(sky_imager.cloud_image)
ax2.imshow(sky_imager.original_image)
ax3.imshow(sky_imager.rotated)
plt.show()

# fig1, (ax1,ax2) = plt.subplots(ncols=2)
# im = ax1.imshow(sky_imager.angle_array[:,:,0])
# fig1.colorbar(im,ax=ax1)
# ax1.set_title("Azimuth", fontsize=25)
#
# im2 = ax2.imshow(sky_imager.angle_array[:,:,1])
# fig1.colorbar(im2,ax=ax2)
# ax2.set_title("Zenith", fontsize=25)
# plt.show()

