from . import Instrument
from . import SkyImager
import os
import glob
from datetime import datetime as dt
import scipy.ndimage
import scipy.signal
import skimage.morphology
import cv2


class SkyImagerSetup(Instrument):
    """
    Class for creating the configuration file for each camera.
    This class only needs to be called once for each camera, as the position
    of the cameras should not change over the project.

    """

    def __init__(self, instrument_name):
        self.instrument_name = self._check_for_instrument(instrument_name)
        super().__init__()
        self.sky_imager = SkyImager(instrument_name)
        self.sun_azimuth_offset = []
        self.sun_elevation_offset = []

    def find_sun(self, img_path, r_thres = 220):
        """
        Method to find the sun in the image which was taken with the gold foil.

        Args:
            path: String of path with the sun picture
            r_thres: Threshold
        """

        self.sky_imager.load_image(img_path,540)
        img = self.sky_imager.original_image
        rows, cols = self.sky_imager.get_image_size()
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), -self.sky_imager.azimuth_offset, 1)
        img = cv2.warpAffine(img, M, (cols, rows))
        img = scipy.ndimage.filters.gaussian_filter(img, 3)
        r_ch = img[:, :, 0]
        sun_filter = r_ch > r_thres
        sun_filter = skimage.morphology.remove_small_objects(sun_filter, 7)
        sun_position = scipy.ndimage.center_of_mass(sun_filter)

        (sun_azimuth_img, sun_elevation_img) = self.sky_imager.pixel_to_ele_azi(sun_position[1],
                                                                                sun_position[0])

        self.sun_azimuth_offset.append(sun_azimuth_img-self.sky_imager.sun_azimuth)
        self.sun_elevation_offset.append(sun_elevation_img-self.sky_imager.sun_elevation)