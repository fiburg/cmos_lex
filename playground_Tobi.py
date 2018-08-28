import cmos
import matplotlib.pyplot as plt


file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_092340_UTCp1.jpg"

sky_imager = cmos.SkyImager("hq")
sky_imager.load_image(file)
sky_imager.crop_image()

plt.imshow(sky_imager.image)
plt.show()

