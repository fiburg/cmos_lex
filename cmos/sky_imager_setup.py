from . import Instrument
from . import SkyImager
import os
import glob
from datetime import datetime as dt
import scipy.ndimage
import scipy.signal
import skimage.morphology


class SkyImagerSetup(Instrument):
    """
    Class for creating the configuration file for each camera.
    This class only needs to be called once for each camera, as the position
    of the cameras should not change over the project.

    """

    def __init__(self, instrument_name):
        self.instrument_name = self._check_for_instrument(instrument_name)
        super().__init__()
        self.sky_imger = SkyImager(instrument_name)

    def find_sun(self, img_path, r_thres = 220):
        """
        Method to find the sun in the image which was taken with the gold foil.

        Args:
            path: String of path with the sun picture
            r_thres: Threshold
        """

        self.sky_imger.load_image(img_path)
        img = self.sky_imger.original_image
        img = scipy.ndimage.filters.gaussian_filter(img, 3)
        r_ch = img[:, :, 0]
        sun_filter = r_ch > r_thres
        sun_filter = skimage.morphology.remove_small_objects(sun_filter, 7)
        sun_position = scipy.ndimage.center_of_mass(sun_filter)

        sun_pos_img = self.sky_imger.pixel_to_ele_azi(sun_position[1],
                                                      sun_position[0])

        return sun_pos_img

        #print((self.sky_imger.sun_azimuth-sun_pos_img[0], self.sky_imger.sun_elevation-sun_pos_img[1]))

        #print('----')

        #self.sun_positions.append([self.sky_imger.date,
        #                           sun_position[1],
        #                           sun_position[0]])