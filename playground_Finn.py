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


#file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_152340_UTCp1.jpg"
#


cloud_height = 2840

file = "/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/img/LEX_WKM2_Image_20180826_152340_UTCp1.jpg"
skyim_hq = cmos.SkyImager("hq")
skyim_hq.load_image(file,cloud_height=cloud_height)
skyim_hq.create_lat_lon_cloud_mask()

file = "/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/img/LEX_WKM3_Image_20180826_152340_UTCp1.jpg"
skyim_west = cmos.SkyImager("west")
skyim_west.load_image(file,cloud_height=cloud_height)
skyim_west.create_lat_lon_cloud_mask()

file = "/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/img/LEX_WKM4_Image_20180826_152340_UTCp1.jpg"
skyim_south = cmos.SkyImager("south")
skyim_south.load_image(file,cloud_height=cloud_height)
skyim_south.create_lat_lon_cloud_mask()

map = cmos.Map(lat_min=11.18, lat_max=11.35, lon_min=54.44, lon_max=54.53)
map.make_map()
map.set_positional_data(date=skyim_hq.date,
                        cloud_height=skyim_hq.cloud_height,
                        sun_azimuth=skyim_hq.sun_azimuth,
                        sun_elevation=skyim_hq.sun_elevation)


map.add_clouds(skyim_hq.lat_lon_cloud_mask, "Reds", vmin=0.)
map.add_station_marker(skyim_hq.instrument_name, skyim_hq.lat, skyim_hq.lon, color='red')

map.add_clouds(skyim_west.lat_lon_cloud_mask, "Blues", vmin=0.)
map.add_station_marker(skyim_west.instrument_name, skyim_west.lat, skyim_west.lon, color='blue')

map.add_clouds(skyim_south.lat_lon_cloud_mask, "Greens", vmin=0.)
map.add_station_marker(skyim_south.instrument_name, skyim_south.lat, skyim_south.lon, color= 'green')

map.add_setting_title('CMOS - Shadow map - HQ, West, South')
map.save_plot("./plot/shadow_map.png")

