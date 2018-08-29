import cmos
import matplotlib.pyplot as plt


path = "/home/fibu/Studium/18_SoSe/Lehrexkursion/cmos_lex/data/alignment/"

sky_imager_corr = cmos.SkyImagerSetup('hq')
sky_imager_corr.find_sun(path)
