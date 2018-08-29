import cmos
import matplotlib.pyplot as plt


file = "/home/fibu/Studium/18_SoSe/Lehrexkursion/Daten/LEX_WKM3_Image_20180826_120000_UTCp1.jpg"

sky_imager = cmos.SkyImager("west")
sky_imager.load_image(file)
sky_imager.crop_image(0)
sky_imager.create_cloud_mask()

print(sky_imager.date)
print(sky_imager.height)
print(sky_imager.sun_elevation, sky_imager.sun_azimuth)

# sky_imager.sun_position_in_image()

fig, (ax1,ax2,ax3) = plt.subplots(ncols=3)
ax1.imshow(sky_imager.original_image)
ax2.imshow(sky_imager.image)
ax3.imshow(sky_imager.cloud_image)
plt.show()