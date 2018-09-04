import cmos
import matplotlib.pyplot as plt
import glob
import os
import numpy as np
import scipy
import cv2


#path = "/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/alignment/"

#sky_imager_corr = cmos.SkyImagerSetup('hq')
#image_path_list = sorted(glob.glob(os.path.join(path, '*.jpg')))

#for img_path in image_path_list:
#    sun_position = sky_imager_corr.find_sun(path)
#    print(sun_position)


#file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_152340_UTCp1.jpg"
#


cloud_height = 2840



#multiplot

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


fig = plt.figure()
map = cmos.Map(lat_min=11.18, lat_max=11.35, lon_min=54.44, lon_max=54.53)
ax = map.make_map(subplot_info=111)

ax.set_positional_data(date=skyim_hq.date,
                        cloud_height=skyim_hq.cloud_height,
                        sun_azimuth=skyim_hq.sun_azimuth,
                        sun_elevation=skyim_hq.sun_elevation)


ax.add_shadows(skyim_hq.lat_lon_cloud_mask, "Reds")
ax.add_station_marker(skyim_hq.instrument_name, skyim_hq.lat, skyim_hq.lon, color='red')

ax.add_shadows(skyim_west.lat_lon_cloud_mask, "Blues")
ax.add_station_marker(skyim_west.instrument_name, skyim_west.lat, skyim_west.lon, color='blue')

ax.add_shadows(skyim_south.lat_lon_cloud_mask, "Greens")
ax.add_station_marker(skyim_south.instrument_name, skyim_south.lat, skyim_south.lon, color= 'green')

ax.add_setting_title('CMOS - Shadow map - HQ, West, South')
plt.tight_layout()
#plt.savefig("./plot/test_shadow_map_corrected_north.png")


"""
# single plot



file = "/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/img/LEX_WKM2_Image_20180826_152340_UTCp1.jpg"

fig = plt.figure(figsize=(21,7))
sky_imager = cmos.SkyImager("hq")

map = cmos.Map()
ceilo = cmos.Ceilometer()

ax1 = plt.subplot(131)
ax2 = plt.subplot(132)
ax3 = map.make_map(subplot_info=133)


sky_imager.load_image(file, cloud_height=cloud_height)

print(sky_imager.date)
print(sky_imager.height)
print(sky_imager.sun_elevation, sky_imager.sun_azimuth)
sky_imager.create_lat_lon_array()
sky_imager.create_lat_lon_cloud_mask()

shadow_on_cam_position = sky_imager.shadow_on_cam_position()
if shadow_on_cam_position:
    base_color = "grey"

else:
    base_color = "darkorange"

print("plotting...")

# Raw image:
ax1.imshow(sky_imager.original_image)


# Cloud Mask:
ax2.imshow(sky_imager.cloud_image)


# Cloud map:
ax3.set_positional_data(date=sky_imager.date,
                        cloud_height=sky_imager.cloud_height,
                        sun_azimuth=sky_imager.sun_azimuth,
                        sun_elevation=sky_imager.sun_elevation)
ax3.add_shadows(sky_imager.lat_lon_cloud_mask)
ax3.add_station_marker(sky_imager.instrument_name, sky_imager.lat, sky_imager.lon, color=base_color)
ax3.add_setting_title('Clouds and shadows', size=16)

plt.savefig('./new_map.png')


#ceilo = cmos.Ceilometer()
#height = ceilo.get_height(skyim_hq.date)
"""

