import cmos
import matplotlib.pyplot as plt
import glob
import os


path = "/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/alignment/"

sky_imager_corr = cmos.SkyImagerSetup('hq')
image_path_list = sorted(glob.glob(os.path.join(path, '*.jpg')))

for img_path in image_path_list:
    sun_position = sky_imager_corr.find_sun(path)
    print(sun_position)

