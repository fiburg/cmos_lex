import cmos
import matplotlib.pyplot as plt
from scipy.ndimage import label
import numpy as np

file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_152340_UTCp1.jpg"

sky_imager = cmos.SkyImager("hq")
sky_imager.load_image(file,cloud_height=2840)

print(sky_imager.date)
print(sky_imager.height)
print(sky_imager.sun_elevation,sky_imager.sun_azimuth)

# sky_imager.sun_position_in_image()

sky_imager.create_lat_lon_array()
sky_imager.create_lat_lon_cloud_mask()

# print(sky_imager.angle_array)

# sky_imager.hemisphere_to_plain(cbh=1000)

fig, (ax1,ax2,ax3) = plt.subplots(ncols=3)
ax1.imshow(sky_imager.original_image)
ax2.imshow(sky_imager.image)
ax3.imshow(sky_imager.cloud_mask[:,:])
plt.show()

fig1, (ax1,ax2) = plt.subplots(ncols=2)
im = ax1.imshow(sky_imager.lat_lon_array[:,:,0])
fig1.colorbar(im,ax=ax1)
ax1.set_title("Latitude", fontsize=25)

im2 = ax2.imshow(sky_imager.lat_lon_array[:,:,1])
fig1.colorbar(im2,ax=ax2)
ax2.set_title("Longitude", fontsize=25)
plt.show()

