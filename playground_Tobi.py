import cmos
import matplotlib.pyplot as plt


file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_092340_UTCp1.jpg"

sky_imager = cmos.SkyImager("hq")
sky_imager.load_image(file)
sky_imager.crop_image(0)
sky_imager.create_cloud_mask()

print(sky_imager.date)
print(sky_imager.height)
print(sky_imager.sun_elevation,sky_imager.sun_azimuth)

# sky_imager.sun_position_in_image()

fig, (ax1,ax2,ax3) = plt.subplots(ncols=3)
ax1.imshow(sky_imager.original_image)
ax2.imshow(sky_imager.image)
ax3.imshow(sky_imager.cloud_image)
plt.show()


