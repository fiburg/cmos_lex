import cmos
import matplotlib.pyplot as plt
import glob
import os
import numpy as np

sky_imager_name = 'west'


path = ('/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/alignment/'+
        sky_imager_name+'/')

sky_imager_corr = cmos.SkyImagerSetup(sky_imager_name)
image_path_list = sorted(glob.glob(os.path.join(path, '*.jpg')))
print(image_path_list)
for img_path in image_path_list:
    sun_position = sky_imager_corr.find_sun(img_path)

print(sky_imager_corr.sun_elevation_offset)
print('----')
print(sky_imager_corr.sun_azimuth_offset)

fig, ax = plt.subplots(nrows=1)
ax.set_xlabel('number of images')
ax.set_ylabel('offset (detect - truth)')
ax.plot(sky_imager_corr.sun_elevation_offset, label='elevation offset')
ax.plot(sky_imager_corr.sun_azimuth_offset, label='azimuth offset')
#ax.set_ylim([3, 7])
ax.legend()
#plt.savefig('./'+sky_imager_name+'_angel_offset.png')

print(np.nanmean(sky_imager_corr.sun_azimuth_offset))
print(np.mean(sky_imager_corr.sun_elevation_offset))
