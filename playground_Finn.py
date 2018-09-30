import cmos
import matplotlib.pyplot as plt
import glob
import os
from datetime import timedelta, datetime
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




#multiplot

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


fig = plt.figure()
map = cmos.Map(lat_min=11.18, lat_max=11.35, lon_min=54.46, lon_max=54.54)
ax = map.make_map(subplot_info=111, tile_resolution=13)

ax.set_positional_data(date=skyim_hq.date,
                        cloud_height=skyim_hq.cloud_height,
                        sun_azimuth=skyim_hq.sun_azimuth,
                        sun_elevation=skyim_hq.sun_elevation)


ax.create_shadow_mask(skyim_hq.lat_lon_cloud_mask)
ax.add_shadows("Reds_r")
ax.add_station_marker(skyim_hq.instrument_name, skyim_hq.lat, skyim_hq.lon, color='red')

ax.create_shadow_mask(skyim_west.lat_lon_cloud_mask)
ax.add_shadows("Blues_r")
ax.add_station_marker(skyim_west.instrument_name, skyim_west.lat, skyim_west.lon, color='blue')

ax.create_shadow_mask(skyim_south.lat_lon_cloud_mask)
ax.add_shadows("Greens_r")
ax.add_station_marker(skyim_south.instrument_name, skyim_south.lat, skyim_south.lon, color='green')

#ax.add_setting_title('CMOS - Shadow map - HQ, West, South')
plt.tight_layout()
plt.savefig("./composit.png", dpi=700)

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
"""
# process whole day
pathHQ = ('/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/img/20180826/hq/')
pathWEST = ('/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/img/20180826/west/')
pathSOUTH = ('/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/img/20180826/south/')

skyim_hq = cmos.SkyImager("hq")
skyim_west = cmos.SkyImager("west")
skyim_south = cmos.SkyImager("south")

map = cmos.Map()
ceilo = cmos.Ceilometer()

start_date = "26.08.2018 10:10:00 +0100"
stop_date = "26.08.2018 13:10:00 +0100"

start = datetime.strptime(start_date, "%d.%m.%Y %H:%M:%S %z")
stop = datetime.strptime(stop_date, "%d.%m.%Y %H:%M:%S %z")

fig = plt.figure()
map = cmos.Map(lat_min=11.16, lat_max=11.30, lon_min=54.47, lon_max=54.53)
ax = map.make_map(subplot_info=111)

while start < stop:
    cloud_height = ceilo.get_height(start)

    skyim_hq = cmos.SkyImager("hq")
    skyim_west = cmos.SkyImager("west")
    skyim_south = cmos.SkyImager("south")

    skyim_hq.load_image((pathHQ+'LEX_WKM2_Image_'+start.strftime('%Y%m%d_%H%M%S')+'_UTCp1.jpg'), cloud_height=cloud_height)
    skyim_hq.create_lat_lon_cloud_mask()

    ax.set_positional_data(date=skyim_hq.date,
                           cloud_height=skyim_hq.cloud_height,
                           sun_azimuth=skyim_hq.sun_azimuth,
                           sun_elevation=skyim_hq.sun_elevation)

    skyim_west.load_image((pathWEST+'LEX_WKM3_Image_'+start.strftime('%Y%m%d_%H%M%S')+'_UTCp1.jpg'), cloud_height=cloud_height)
    skyim_west.create_lat_lon_cloud_mask()

    skyim_south.load_image((pathSOUTH+'LEX_WKM4_Image_'+start.strftime('%Y%m%d_%H%M%S')+'_UTCp1.jpg'), cloud_height=cloud_height)
    skyim_south.create_lat_lon_cloud_mask()

    ax.add_shadows(skyim_hq.lat_lon_cloud_mask, "Reds")
    ax.add_shadows(skyim_west.lat_lon_cloud_mask, "Blues")
    ax.add_shadows(skyim_south.lat_lon_cloud_mask, "Greens")

    if skyim_hq.shadow_on_cam_position():
        base_color_hq = "grey"
    else:
        base_color_hq = "yellow"

    if skyim_west.shadow_on_cam_position():
        base_color_west = "grey"
    else:
        base_color_west = "yellow"

    if skyim_south.shadow_on_cam_position():
        base_color_south = "grey"
    else:
        base_color_south = "yellow"

    ax.add_station_marker(skyim_hq.instrument_name, skyim_hq.lat,
                           skyim_hq.lon, color=base_color_hq)
    ax.add_station_marker(skyim_west.instrument_name, skyim_west.lat,
                          skyim_west.lon, color=base_color_west)
    ax.add_station_marker(skyim_south.instrument_name, skyim_south.lat,
                          skyim_south.lon, color=base_color_south)

    ax.add_setting_title('Clouds and shadows', size=16)

    plt.tight_layout()
    plt.savefig('./plot/comp/comp_shadows_'+start.strftime('%Y%m%d_%H%M%S')+'.png')

    skyim_hq = None
    skyim_west = None
    skyim_south = None

    ax.remove_sky_values()


    start = start + timedelta(seconds=20)
"""