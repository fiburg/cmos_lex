import cmos
import matplotlib.pyplot as plt
from scipy.ndimage import label

file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_152340_UTCp1.jpg"

sky_imager = cmos.SkyImager("hq")
sky_imager.load_image(file)
sky_imager.crop_image(0)
sky_imager.create_cloud_mask()

print(sky_imager.date)
print(sky_imager.height)
print(sky_imager.sun_elevation,sky_imager.sun_azimuth)

# sky_imager.sun_position_in_image()

sky_imager.create_angle_array()

# print(sky_imager.angle_array)



fig, (ax1,ax2,ax3) = plt.subplots(ncols=3)
ax1.imshow(sky_imager.original_image)
ax2.imshow(sky_imager.image)
ax3.imshow(sky_imager.cloud_image)
plt.show()

fig1, (ax1,ax2) = plt.subplots(ncols=2)
im = ax1.imshow(sky_imager.angle_array[:,:,0])
fig1.colorbar(im,ax=ax1)
ax1.set_title("Azimuth Angle", fontsize=25)

im2 = ax2.imshow(sky_imager.angle_array[:,:,1])
fig1.colorbar(im2,ax=ax2)
ax2.set_title("Elevation Angle", fontsize=25)
plt.show()

