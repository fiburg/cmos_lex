from PIL import Image
import numpy as np
from . import Instrument
import pysolar
import os
from datetime import datetime as dt
import datetime
from pytz import timezone
import scipy

class SkyImager(Instrument):
    """
    Class to process the Allsky Images.
    This Class takes the raw input image and is capable of
    - rotating it to have the right north-angle

    """

    def __init__(self, instrument_name):
        self.instrument_name = self._check_for_instrument(instrument_name)
        super().__init__()
        self.image = None
        self.cloud_image = None
        self.original_image = None
        self.angle_array = None
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
        self._apply_rotation_calib()
        self.remove_sun()

    def _get_date_from_image_name(self):
        """
        sets the self.date by reading the name of the input file.

        """

        filename = os.path.split(self.input_file)[-1]
        _date = "_".join(filename.split("_")[3:5])
        self.date = dt.strptime(_date,"%Y%m%d_%H%M%S")
        self.date = self.date - datetime.timedelta(hours=1)
        self.date.replace(tzinfo=timezone("UTC"))

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
        """
        get the length along both axes of the input image.

        Returns:
            tuple of (x_size, y_size)
        """
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
        """
        Creates an array self.cloud_image where clouds are masked, based on some
        sky index (SI) and brightness index (BI).

        Returns:

        """


        image_f = self.image.astype(float)

        SI = ((image_f[:, :, 2]) - (image_f[:, :, 0])) / (
            ((image_f[:, :, 2]) + (image_f[:, :, 0])))

        SI[np.isnan(SI)] = 1

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

        sun_azimuth = pysolar.solar.get_azimuth(latitude_deg=self.lat, longitude_deg=self.lon,
                                   when=self.date, elevation=self.height)

        if sun_azimuth < 0:
            if (sun_azimuth >= -180):
                solarheading = ((sun_azimuth * -1) + 180)
            if (sun_azimuth < -180):
                solarheading = ((sun_azimuth * -1) - 180)
            if sun_azimuth >= 0:
                solarheading = sun_azimuth

        self.sun_azimuth = solarheading


    def create_angle_array(self):
        """
        Creates an array in which the azimuth and elevation angles are the values
        The 0 dimension is th azimuth
        The 1 dimension is the elevation

        The values are for a theoretically perfect alligned and turned image!

        Examples:
            To get the elevation over the whole allskyimage :

            >>> plt.imshow(self.angle_array[:,:,1])



        Returns:
            sets the self.angle_array

        """
        x_size, y_size = self.get_image_size()

        angle_array = np.zeros([x_size,y_size,2])

        xx, yy = np.meshgrid(range(x_size),range(y_size), sparse=True)

        x_dash = self._convert_var_to_dash(xx)
        y_dash = self._convert_var_to_dash(yy)

        # Azimuth angle:
        angle_array[xx,yy,0] = SkyImager._azimuth_angle(x_dash,y_dash)
        angle_array[:,:,0] = np.subtract(angle_array[:,:,0],90)
        negative_mask = angle_array[:, :, 0] < 0
        angle_array[:, :, 0][negative_mask] = np.add(angle_array[:, :, 0][negative_mask],360)

        # Elevation angle:
        angle_array[xx,yy,1] = self._elevation_angle(x_dash,y_dash)
        angle_array[:,:,1] = np.subtract(angle_array[:,:,1],90)
        angle_array[:,:,1] = np.negative(angle_array[:,:,1])


        self.angle_array = angle_array

    def pixel_to_ele_azi(self,x,y):
        """
        Method to get the azimuth and elevation of a single allsky-image pixel.

        Args:
            x: position pixel in x direction
            y: position pixel in y direction

        Returns:
            tuple of (azimuth, elevation)
        """

        x_dash = self._convert_var_to_dash(x)
        y_dash= self._convert_var_to_dash(y)

        azimuth = SkyImager._azimuth_angle(x_dash,y_dash)
        azimuth -= 90
        if azimuth < 0 :
            azimuth += 360

        elevation = self._elevation_angle(x_dash,y_dash)
        elevation -= 90
        elevation *= -1

        return (azimuth, elevation)


    def _convert_var_to_dash(self,var):
        """
        This function converts a variable x or y to be dependent on the center:

            x' = x - a
            y* = y - a

        Args:
            var: x or y

        Returns: x' or y'

        """
        a = self.get_image_size()[0] / 2
        return var - a


    @staticmethod
    def _azimuth_angle(x_dash,y_dash):
        """
        calculates the azimuth angle in the picture from coordinates x' and y'


        Args:
            x_dash: x'
            y_dash: y'

        Returns:
            azimuth angle alpha of the coordinates x' and y'.

        """
        return np.rad2deg(np.arctan2(x_dash,y_dash))


    def _elevation_angle(self,x_dash,y_dash):
        """
        calculates the elevation angle in the picture from coordinates x' and y'

        Args:
            x_dash: x'
            y_dash: y'

        Returns:
            elevation angle epsilon of the coordinates x' and y'.

        """
        a = self.get_image_size()[0]/2
        r = SkyImager._calc_radius(x_dash,y_dash)
        return np.multiply(90, (1 - np.divide(r, a)))

    @staticmethod
    def _calc_radius(x,y):
        """
        calculates the radius from x and y:

        r = sqrt(x² + y²)

        Args:
            x:
            y:

        Returns:
            radius r.
        """
        return np.sqrt(np.power(x,2) + np.power(y,2))

    @staticmethod
    def find_nearest_idx(array1,array2, value1,value2):
        """
        finds the nearest coordinates in two array representing the azimuth and
        elevation.

        Args:
            array1: array containing azimuth angles
            array2: array containing elevation angles
            value1: azimuth angle of the coordinates to be found in the arrays
            value2: elevation angle of the coordinates to be found in the arrays

        Returns:
            the index of the coordinates where the values are closest to the arrays.

        """
        temp = np.sqrt(np.square(array1 - value1) + np.square(array2 - value2))
        idx = np.where(temp == temp.min())
        return idx


    def remove_sun(self):
        """
        Calculates the center of the sun inside the image
        and draws a circle around it.

        """

        if not self.angle_array:
            self.create_angle_array()



        sun_pos = self.find_nearest_idx(self.angle_array[:,:,0],self.angle_array[:,:,1],
                                        self.sun_azimuth,self.sun_elevation)



        ###-----------Draw circle around position of sun-------------------------------------------------------------------------------------------


        x_sol_cen = int(sun_pos[0])
        y_sol_cen = int(sun_pos[1])
        Radius_sol = 300
        Radius_sol_center = 250

        x_size, y_size = self.get_image_size()


        y, x = np.ogrid[-y_sol_cen:y_size - y_sol_cen, -x_sol_cen:x_size - x_sol_cen]
        sol_mask = x ** 2 + y ** 2 <= Radius_sol ** 2
        sol_mask_cen = x ** 2 + y ** 2 <= Radius_sol_center ** 2
        sol_mask_cen1 = np.logical_xor(sol_mask_cen, sol_mask)
        self.image[:, :, :][sol_mask_cen1] = [0, 0, 0]



    def _rotate_image(self, deg):
        self.image = scipy.ndimage.rotate(self.image,angle=deg)

    def _apply_rotation_calib(self):
        # self._rotate_image()
        pass


    def hemisphere_to_plain(self,cbh):
        pass
        # alpha, epsilon = self.pixel_to_ele_azi(x,y)
        # r_hut = cbh * np.tan(np.deg2rad(90) - epsilon)



