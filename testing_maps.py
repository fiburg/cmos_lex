import cmos
import matplotlib.pyplot as plt

# file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_112340_UTCp1.jpg"


cmos.live_plot("./map.jpg", "W:/Aufzeichnung/wkm2/jpg/LEX_WKM2_Image_*_UTCp1.jpg")

# cmos.live_plot("./map.jpg", "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_112520_UTCp1.jpg")

plt.show()