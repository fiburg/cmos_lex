from PIL import Image
import numpy as np
from . import Instrument
import pysolar
import os
from datetime import datetime as dt


class SkyImager(Instrument):
    """
    Class to process the Allsky Images.
    This Class takes the raw input image and is capable of
    - rotating it to have the right north-angle
    -

    """

    def __init__(self,instrument_name):
        super().__init__()
        self.instrument_name = self._check_for_instrument(instrument_name)
        self.image = None
        self.cloud_image = None
        self.original_image = None
        self.scale_factor = None
        self.input_file = None

        self.sun_azimuth = None
        self.sun_elevation = None

    def load_image(self, input_file, scale_factor=100):
        """
        Routine zum einlesen einer .png datei. Diese wird als numpy array
        zurückgegeben.

        Args:
            inputFile: str: Pfad und Name des Bildes
            scale_factor: float: Skalierungsfaktor in %. 100=original, 50=halbe Pixelzahl.

        Returns:
            Numpy array mit shape:(3,breite,höhe), sodass mit dem ersten index farbwert abgegriffen wird.

        """
        self.input_file = input_file
        image_raw = Image.open(input_file)
        x_size_raw = image_raw.size[0]
        y_size_raw = image_raw.size[1]
        set_scale_factor = (scale_factor / 100.)

        new_size = (x_size_raw * set_scale_factor, y_size_raw * set_scale_factor)
        image_raw.thumbnail(new_size, Image.ANTIALIAS)

        image_array = np.asarray(image_raw, order='F')
        image_array.setflags(write=True)

        self.image = image_array
        self.original_image = self.image.copy()
        self.scale_factor = scale_factor

        self._get_date_from_image_name()
        self.get_sun_position()
        self.remove_sun()

    def _get_date_from_image_name(self):
        """
        sets the self.date by reading the name of the input file.

        """

        filename = os.path.split(self.input_file)[-1]
        _date = "_".join(filename.split("_")[3:5])
        self.date = dt.strptime(_date,"%Y%m%d_%H%M%S")

    def find_center(self):
        """
        Find the position (x,y) of the center of an array.

        Args:
            img_array: array of the image

        Returns: tuple: center of the image.
        """
        center_x = int(np.divide(self.image.shape[0], 2))
        center_y = int(np.divide(self.image.shape[1], 2))

        return (center_x,center_y)

    def get_image_size(self):
        x_size = self.image.shape[0]
        y_size = self.image.shape[1]

        return (x_size,y_size)

    def crop_image(self, elevation=30):
        """
        Crops the image, so that only the center is being used.
        An elevation angle of 30 would mean, that everything below 30 degrees
        elevation will be cut away, leaving an opening angle of 120 degrees.

        Args:
            elevation: Angle at which the image will be cut.

        """

        x_center, y_center = self.find_center()
        x_size, y_size = self.get_image_size()
        y, x = np.ogrid[-y_center:y_size - y_center, -x_center:x_size - x_center]

        crop_size = x_size/2 - (x_size/2 / 90 * elevation)

        center_mask = x ** 2 + y ** 2 <= (crop_size) ** 2
        self.image[:,:,:][~center_mask] = [0,0,0]

    def _read_lense_settings(self):
        pass

    def create_cloud_mask(self):

        image_f = self.image.astype(float)

        SI = ((image_f[:, :, 2]) - (image_f[:, :, 0])) / (
            ((image_f[:, :, 2]) + (image_f[:, :, 0])))

        SI[np.isnan(SI)] = 1
        print(np.where(SI < 1))

        mask_sol1 = SI < 0.1
        Radius = 990

        x_center, y_center = self.find_center()
        x_size, y_size = self.get_image_size()
        y, x = np.ogrid[-y_center:y_size - y_center, -x_center:x_size - x_center]
        # sol_mask_double = x ** 2 + y ** 2 <= Radius ** 2
        # mask_sol1 = np.logical_and(mask_sol1)
        self.cloud_image = self.image.copy()
        self.cloud_image[:, :, :][mask_sol1] = [255, 0, 0]

    def get_sun_position(self):
        """
        Calculates the theoretic position of the sun by the lon, lat height and
        date of the image.

        """
        self.sun_elevation = pysolar.solar.get_altitude(latitude_deg=self.lat, longitude_deg=self.lon,
                                   when=self.date, elevation=self.height)

        self.sun_azimuth = pysolar.solar.get_azimuth(latitude_deg=self.lat, longitude_deg=self.lon,
                                   when=self.date, elevation=self.height)

    def remove_sun(self):
        """
        Calculates the center of the sun inside the image.

        Returns: x,y pixel of center of the sun.

        """

        azimuth = self.sun_azimuth

        azimuth -= 90
        if azimuth < 0:
            azimuth *= (-1)

        AzimutWinkel = ((2 * np.pi) / 360) * (azimuth - 90)
        sza = ((2 * np.pi) / 360) * azimuth

        x_center, y_center = self.find_center()

        x_sol_cen = x_center
        y_sol_cen = y_center
        RadiusBild = self.get_image_size()[0]/2
        sza_dist = RadiusBild * np.cos(sza)

        x = x_sol_cen - sza_dist * np.cos(AzimutWinkel + np.deg2rad(180))
        y = y_sol_cen - sza_dist * np.sin(AzimutWinkel + np.deg2rad(180))

        ###-----------Draw circle around position of sun-------------------------------------------------------------------------------------------


        x_sol_cen = int(x)
        y_sol_cen = int(y)
        Radius_sol = 300
        Radius_sol_center = 250

        x_size, y_size = self.get_image_size()


        y, x = np.ogrid[-y_sol_cen:y_size - y_sol_cen, -x_sol_cen:x_size - x_sol_cen]
        sol_mask = x ** 2 + y ** 2 <= Radius_sol ** 2
        sol_mask_cen = x ** 2 + y ** 2 <= Radius_sol_center ** 2
        sol_mask_cen1 = np.logical_xor(sol_mask_cen, sol_mask)
        self.image[:, :, :][sol_mask_cen1] = [0, 0, 0]




