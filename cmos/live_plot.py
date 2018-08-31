import cmos
import matplotlib.pyplot as plt
import glob
import os
import numpy as np
import time


def live_plot(output_path, image_folder):
    files = image_folder
    sky_imager = cmos.SkyImager("hq")
    map = cmos.Map()
    map.make_map()

    while True:
        file = sorted(glob.glob(files))[-1]
        print(file)

        sky_imager.load_image(file, cloud_height=640)
        print(sky_imager.date)
        print(sky_imager.height)
        print(sky_imager.sun_elevation, sky_imager.sun_azimuth)
        sky_imager.create_lat_lon_array()
        sky_imager.create_lat_lon_cloud_mask()

        map.set_positional_data(date=sky_imager.date,
                                cloud_height=sky_imager.cloud_height,
                                sun_azimuth=sky_imager.sun_azimuth,
                                sun_elevation=sky_imager.sun_elevation)
        map.add_shadows(sky_imager.lat_lon_cloud_mask)
        map.add_clouds(sky_imager.lat_lon_cloud_mask)
        map.add_station_marker(sky_imager.instrument_name, sky_imager.lat, sky_imager.lon)
        map.add_setting_title('CMOS - Clouds and shadows - HQ sky imager')
        map.save_plot(output_path)
        map.remove_sky_values()

        # plt.show()
        print("sleeping")
        time.sleep(60)
        print("sleeping done")
        # plt.close()

