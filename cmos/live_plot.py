import cmos
import matplotlib.pyplot as plt
import glob
import os
import numpy as np
import time


def live_plot(output_path, image_folder):
    while True:
        #path = "/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/alignment/"

        #sky_imager_corr = cmos.SkyImagerSetup('hq')
        #image_path_list = sorted(glob.glob(os.path.join(path, '*.jpg')))

        #for img_path in image_path_list:
        #    sun_position = sky_imager_corr.find_sun(path)
        #    print(sun_position)

        # file = "/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/img/LEX_WKM2_Image_20180826_152340_UTCp1.jpg"
        # files = "W:/Aufzeichnung/wkm2/jpg/LEX_WKM2_Image_*_UTCp1.jpg"

        files = image_folder

        file = sorted(glob.glob(files))[-1]
        print(file)

        sky_imager = cmos.SkyImager("hq")
        sky_imager.load_image(file, cloud_height=640)

        print(sky_imager.date)
        print(sky_imager.height)
        print(sky_imager.sun_elevation, sky_imager.sun_azimuth)

        sky_imager.create_lat_lon_array()
        sky_imager.create_lat_lon_cloud_mask()

        map = cmos.Map()

        map.make_map()
        map.set_positional_data(date=sky_imager.date,
                                cloud_height=sky_imager.cloud_height,
                                sun_azimuth=sky_imager.sun_azimuth,
                                sun_elevation=sky_imager.sun_elevation)
        map.add_shadows(sky_imager.lat_lon_cloud_mask)
        map.add_clouds(sky_imager.lat_lon_cloud_mask)
        map.add_station_marker(sky_imager.instrument_name, sky_imager.lat, sky_imager.lon)
        map.add_setting_title('CMOS - Clouds and shadows - HQ sky imager')
        map.save_plot(output_path)

        # plt.show()
        print("sleeping")
        time.sleep(60)
        print("sleeping done")
        # plt.close()

