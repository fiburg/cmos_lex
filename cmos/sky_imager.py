from PIL import Image
import numpy as np
from . import Instrument
import pysolar
import os
from datetime import datetime as dt
import datetime
from pytz import timezone
import scipy
import collections
import geopy
import cmos

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
        self.cloud_mask = None
        self.lat_lon_cloud_mask = None
        self.lat_lon_array = None

        self.scale_factor = None
        self.crop_elevation = None

        self.input_file = None

        self.cloud_height = None

        self.sun_azimuth = None
        self.sun_elevation = None

    def load_image(self, input_file,cloud_height, scale_factor=100, crop_elevation=30):
        """
        Routine zum einlesen einer .png datei. Diese wird als numpy array
        zurückgegeben.

        Args:
            input_file: str: Pfad und Name des Bildes
            scale_factor: float: Skalierungsfaktor in %. 100=original, 50=halbe Pixelzahl.

        Returns:
            Numpy array mit shape:(3,breite,höhe), sodass mit dem ersten index farbwert abgegriffen wird.

        """
        self.input_file = input_file
        self.cloud_height = cloud_height
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

        self.crop_elevation = crop_elevation

        self._get_date_from_image_name()
        self.get_sun_position()
        self.remove_sun()
        self.image = self.crop_image(self.image, self.crop_elevation)
        self._apply_rotation_calib()
        self.create_cloud_mask()
        # self.create_lat_lon_cloud_mask()


    def _get_date_from_image_name(self):
        """
        sets the self.date by reading the name of the input file.

        """

        filename = os.path.split(self.input_file)[-1]
        _date = "_".join(filename.split("_")[3:5])
        self.date = dt.strptime(_date, "%Y%m%d_%H%M%S")
        self.date = self.date - datetime.timedelta(hours=1)
        self.date = self.date.replace(tzinfo=timezone("UTC"))

    def find_center(self):
        """
        Find the position (x,y) of the center of an array.

        Returns: tuple: center of the image.
        """
        center_x = int(np.divide(self.image.shape[0], 2))
        center_y = int(np.divide(self.image.shape[1], 2))

        return center_x, center_y

    def get_image_size(self):
        """
        get the length along both axes of the input image.

        Returns:
            tuple of (x_size, y_size)
        """
        x_size = self.image.shape[0]
        y_size = self.image.shape[1]

        return x_size, y_size

    def crop_image(self, image, elevation=30, crop_value=0):
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

        crop_size = x_size / 2 - (x_size / 2 / 90 * elevation)

        center_mask = x ** 2 + y ** 2 <= (crop_size) ** 2

        print("DIMENSION: ", np.ndim(image))
        if np.shape(image)[2] == 3:
            image[:,:,:][~center_mask] = [crop_value,crop_value,crop_value]
        elif np.shape(image)[2] == 2:
            print("Cropping image!")
            image[:, :][~center_mask] = [crop_value,crop_value]
        elif np.ndim(image) == 2:
            print("Cropping image!")
            image[:, :][~center_mask] = crop_value
        else:
            raise IndexError("For this index the cropping is not implemented yet.")

        return image

    def _read_lense_settings(self):
        pass

    def create_cloud_mask(self):
        """
        Creates an array self.cloud_image where clouds are masked, based on some
        sky index (SI) and brightness index (BI).

        Returns:

        """

        image_f = self.image.astype(float)
        # image_f = self.crop_image(image_f,elevation=5)

        SI = ((image_f[:, :, 2]) - (image_f[:, :, 0])) / (
            ((image_f[:, :, 2]) + (image_f[:, :, 0])))

        SI[np.isnan(SI)] = 1

        mask_sol1 = SI < 0.12
        Radius = 990

        x_center, y_center = self.find_center()
        x_size, y_size = self.get_image_size()
        y, x = np.ogrid[-y_center:y_size - y_center, -x_center:x_size - x_center]
        # sol_mask_double = x ** 2 + y ** 2 <= Radius ** 2
        # mask_sol1 = np.logical_and(mask_sol1)
        self.cloud_image = self.image.copy()
        self.cloud_image[:, :, :][mask_sol1] = [255, 0, 0]
        self.cloud_mask = self.cloud_image[:,:,0].copy()
        self.cloud_mask[:,:] = 0
        self.cloud_mask[:,:][mask_sol1] = 1

    def create_lat_lon_cloud_mask(self):
        if not isinstance(self.image,collections.Iterable):
            raise NotImplementedError("No image loaded yet. Image needs to be loaded first using the load_image method.")

        if not isinstance(self.lat_lon_array, collections.Iterable):
            self.create_lat_lon_array()

        if not isinstance(self.cloud_mask,collections.Iterable):
            self.create_cloud_mask()


        self.lat_lon_cloud_mask = self.image.copy().astype(float)
        self.lat_lon_cloud_mask[:,:,:] = np.nan
        self.lat_lon_cloud_mask[:,:,0] = self.cloud_mask[:,:]
        self.lat_lon_cloud_mask[:,:,1] = self.lat_lon_array[:,:,0]
        self.lat_lon_cloud_mask[:,:,2] = self.lat_lon_array[:,:,1]

    def create_lat_lon_array(self):
        """
        Using the angle array and a height creating a similar aray containing the lat and lon values of each pixel.

        Returns:

        """
        if not isinstance(self.image,collections.Iterable):
            raise NotImplementedError("No image loaded yet. Image needs to be loaded first using the load_image method.")

        if not isinstance(self.angle_array, collections.Iterable):
            self.create_angle_array()

        dist = np.multiply(np.tan(np.deg2rad(self.angle_array[:,:,1])),self.cloud_height)

        # print("DIST: ", np.min(dist))

        dx = np.multiply(dist, np.sin(np.deg2rad(self.angle_array[:,:,0]))) # azimuth measured clockwise from due north
        dy = np.multiply(dist, np.cos(np.deg2rad(self.angle_array[:,:,0]))) # dx, dy same units as R

        # print("DX DY: ", np.min(dx), np.min(dy))

        delta_longitude = np.divide(dx, (np.multiply(111320, np.cos(np.deg2rad(self.lat)))) )#dx, dy in meters
        delta_latitude = np.divide(dy, 110540) # result in degrees long / lat

        # print("DELTA LATLON: ", np.min(delta_latitude),np.min(delta_longitude))

        final_longitude = np.add(self.lon, delta_longitude)
        final_latitude = np.add(self.lat, delta_latitude)

        # print("FINAL LATLON: ", np.min(final_latitude), np.min(final_longitude))

        self.lat_lon_array = self.image[:,:,:2].copy().astype(float)
        self.lat_lon_array[:,:,:] = np.nan
        self.lat_lon_array[:,:,0] = final_latitude
        self.lat_lon_array[:,:,1] = final_longitude

        self.lat_lon_array = self.crop_image(self.lat_lon_array, crop_value=np.nan)


    def get_sun_position(self):
        """
        Calculates the theoretic position of the sun by the lon, lat height and
        date of the image.

        """
        sun_elevation = pysolar.solar.get_altitude(latitude_deg=self.lat, longitude_deg=self.lon,
                                                        when=self.date, elevation=self.height)

        sun_elevation = 90 - sun_elevation
        self.sun_elevation =  sun_elevation

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

        angle_array = np.zeros([x_size, y_size, 2])

        xx, yy = np.meshgrid(range(x_size), range(y_size), sparse=True)

        x_dash = self._convert_var_to_dash(xx)
        y_dash = self._convert_var_to_dash(yy)

        # Azimuth angle:
        angle_array[xx, yy, 0] = SkyImager._azimuth_angle(x_dash, y_dash)
        angle_array[:, :, 0] = np.subtract(angle_array[:, :, 0], 90)
        negative_mask = angle_array[:, :, 0] < 0
        angle_array[:, :, 0][negative_mask] = np.add(angle_array[:, :, 0][negative_mask], 360)
        angle_array = np.fliplr(angle_array)

        # Elevation angle:
        angle_array[xx, yy, 1] = self._elevation_angle(x_dash, y_dash)
        angle_array[:, :, 1] = np.subtract(angle_array[:, :, 1], 90)
        angle_array[:, :, 1] = np.negative(angle_array[:, :, 1])

        self.angle_array = self.crop_image(angle_array,elevation=self.crop_elevation,crop_value=0)

    def ele_azi_to_pixel(self,azimuth,elevation):
        x_size, y_size = self.get_image_size()

        r = x_size/2 * ( 1 - ((90-elevation)/90))

        x = r * np.sin(np.deg2rad(azimuth)) + x_size/2
        y = r * np.cos(np.deg2rad(azimuth)) + x_size/2

        return int(round(x,0)),int(round(y,0))




    def pixel_to_ele_azi(self, x, y):
        """
        Method to get the azimuth and elevation of a single allsky-image pixel.

        Args:
            x: position pixel in x direction
            y: position pixel in y direction

        Returns:
            tuple of (azimuth, elevation)
        """

        x_dash = self._convert_var_to_dash(x)
        y_dash = self._convert_var_to_dash(y)

        azimuth = SkyImager._azimuth_angle(x_dash, y_dash)
        if azimuth < 0:
            azimuth += 360



        elevation = self._elevation_angle(x_dash, y_dash)
        elevation -= 90
        elevation *= -1

        return azimuth, elevation

    def _convert_var_to_dash(self, var):
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
    def _azimuth_angle(x_dash, y_dash):
        """
        calculates the azimuth angle in the picture from coordinates x' and y'


        Args:
            x_dash: x'
            y_dash: y'

        Returns:
            azimuth angle alpha of the coordinates x' and y'.

        """
        return np.rad2deg(np.arctan2(x_dash, y_dash))

    def _elevation_angle(self, x_dash, y_dash):
        """
        calculates the elevation angle in the picture from coordinates x' and y'

        Args:
            x_dash: x'
            y_dash: y'

        Returns:
            elevation angle epsilon of the coordinates x' and y'.

        """
        a = self.get_image_size()[0] / 2
        r = SkyImager._calc_radius(x_dash, y_dash)

        return np.multiply(90, (1 - np.divide(r, a)))

    @staticmethod
    def _calc_radius(x, y):
        """
        calculates the radius from x and y:

        r = sqrt(x² + y²)

        Args:
            x:
            y:

        Returns:
            radius r.
        """
        return np.sqrt(np.power(x, 2) + np.power(y, 2))

    @staticmethod
    def find_nearest_idx(array1, array2, value1, value2):
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
        temp = np.sqrt(np.square(np.subtract(array1 ,value1)) + np.square(np.subtract(array2, value2)))
        idx = np.where(temp == temp.min())
        return idx

    def remove_sun(self):
        """
        Calculates the center of the sun inside the image
        and draws a circle around it.

        """

        if not isinstance(self.angle_array, collections.Iterable):
            self.create_angle_array()

        # sun_pos = self.find_nearest_idx(self.angle_array[:, :, 0], self.angle_array[:, :, 1],
        #                                 self.sun_azimuth, self.sun_elevation)

        #-----------Draw circle around position of sun--------------------------------------------------------------

        # x_sol_cen, y_sol_cen = sun_pos
        x_sol_cen, y_sol_cen = self.ele_azi_to_pixel(self.sun_azimuth,self.sun_elevation)

        print("X_SOL_CEN", x_sol_cen, y_sol_cen)
        Radius_sol = 300
        Radius_sol_center = 0

        x_size, y_size = self.get_image_size()

        y, x = np.ogrid[-y_sol_cen:y_size - y_sol_cen, -x_sol_cen:x_size - x_sol_cen]
        sol_mask = x ** 2 + y ** 2 <= Radius_sol ** 2
        sol_mask_cen = x ** 2 + y ** 2 <= Radius_sol_center ** 2
        sol_mask_cen1 = np.logical_xor(sol_mask_cen, sol_mask)
        self.image[:, :, :][sol_mask_cen1] = [0, 0, 0]

    def _rotate_image(self, deg):
        self.image = scipy.ndimage.rotate(self.image, angle=deg)

    def _apply_rotation_calib(self):
        # self._rotate_image()
        pass


    def shadow_on_cam_position(self):

        if not isinstance(self.lat_lon_cloud_mask, collections.Iterable):
            self.create_lat_lon_cloud_mask()

        map = cmos.Map()
        map.sun_elevation = self.sun_elevation
        map.sun_azimuth = self.sun_azimuth
        map.cloud_height = self.cloud_height

        cloud_above_cam = self.lat_lon_cloud_mask.copy()
        cloud_above_cam[:,:,0][self.angle_array[:,:,1] > 2] = 0
        cloud_above_cam[np.isnan(cloud_above_cam)] = 0



        # print("CLOUD_ABOVE_CAM:", cloud_above_cam.shape)
        print(np.where(cloud_above_cam >0))
        shadow_above_cam = map.calculate_shadow_offset(cloud_above_cam)
        # print("SHAPE:",shadow_above_cam.shape)
        # print("Shadow_above_cam",shadow_above_cam[np.where(shadow_above_cam[:,:,0] > 0)].shape)


        shadow_index_at_cam = np.nansum(shadow_above_cam[:,:,0])
        print("SHADOWINDEX:",shadow_index_at_cam)

        if shadow_index_at_cam > 100:
            print("Shadow!")
            return 1

        else:
            print("NO Shadow!")
            return 0