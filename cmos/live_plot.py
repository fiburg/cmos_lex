import cmos
import matplotlib.pyplot as plt
import glob
import os
import numpy as np
import time


def live_plot(output_path, image_folder):

    fig = plt.figure(figsize=(21,7))
    files = image_folder
    sky_imager = cmos.SkyImager("hq")
    map = cmos.Map()
    ceilo = cmos.Ceilometer()

    ax1 = plt.subplot(131)
    ax2 = plt.subplot(132)
    ax3 = map.make_map(subplot_info=133)


    while True:
        print(files)
        file = sorted(glob.glob(files))[-1]
        print(file)

        sky_imager.get_date_from_image_name(file)
        cloud_height = ceilo.get_height(sky_imager.date)
        print('cloud height = ' + str(cloud_height))

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
        ax3.create_shadow_mask(sky_imager.lat_lon_cloud_mask)
        ax3.add_shadows()
        # ax3.add_clouds(sky_imager.lat_lon_cloud_mask)
        ax3.add_station_marker(sky_imager.instrument_name, sky_imager.lat, sky_imager.lon, color=base_color)
        ax3.add_setting_title('Clouds and shadows', size=16)

        print("Saving image...")
        plt.savefig(output_path)

        print("Removing old layers from Map...")
        ax3.remove_sky_values()
        map.remove_sky_values()

        # plt.show()
        print("sleeping")
        time.sleep(10)
        print("sleeping done")

        # plt.close()

