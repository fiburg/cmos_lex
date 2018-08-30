import cmos
import matplotlib.pyplot as plt
import glob
import os
import numpy as np


#path = "/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/alignment/"

#sky_imager_corr = cmos.SkyImagerSetup('hq')
#image_path_list = sorted(glob.glob(os.path.join(path, '*.jpg')))

#for img_path in image_path_list:
#    sun_position = sky_imager_corr.find_sun(path)
#    print(sun_position)

file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_152340_UTCp1.jpg"

sky_imager = cmos.SkyImager("hq")
sky_imager.load_image(file,cloud_height=2840)

print(sky_imager.date)
print(sky_imager.height)
print(sky_imager.sun_elevation,sky_imager.sun_azimuth)

sky_imager.create_lat_lon_array()
sky_imager.create_lat_lon_cloud_mask()

map = cmos.Map()

print(sky_imager.lat_lon_cloud_mask[:,:,1])
map.load_cloud_mask(sky_imager.lat_lon_cloud_mask,
                    cloud_height=sky_imager.cloud_height,
                    date=sky_imager.date,
                    sun_azimuth=sky_imager.sun_azimuth,
                    sun_elevation=sky_imager.sun_elevation)
map.plot_map("./plot/map.png")

