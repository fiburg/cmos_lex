from PIL import Image
import numpy as np
from . import Instrument

class SkyImager(Instrument):
    """
    Class to process the Allsky Images.
    This Class takes the raw input image and is capable of
    - rotating it to have the right north-angle
    -

    """

    def __init__(self,instrument_name):
        self.instrument_name = self._check_for_instrument(instrument_name)
        self.image = None
        self.scale_factor = None




    def load_image(self,input_file, scale_factor=100):
        """
        Routine zum einlesen einer .png datei. Diese wird als numpy array
        zurückgegeben.

        Args:
            inputFile: str: Pfad und Name des Bildes
            scale_factor: float: Skalierungsfaktor in %. 100=original, 50=halbe Pixelzahl.

        Returns:
            Numpy array mit shape:(3,breite,höhe), sodass mit dem ersten index farbwert abgegriffen wird.

        """
        image_raw = Image.open(input_file)
        x_size_raw = image_raw.size[0]
        y_size_raw = image_raw.size[1]
        set_scale_factor = (scale_factor / 100.)

        new_size = (x_size_raw * set_scale_factor, y_size_raw * set_scale_factor)
        image_raw.thumbnail(new_size, Image.ANTIALIAS)

        image_array = np.asarray(image_raw, order='F')
        image_array.setflags(write=True)

        self.image = image_array
        self.scale_factor = scale_factor


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

        Returns:

        """
        pass


        x_center, y_center = self.find_center()
        x_size, y_size = self.get_image_size()
        y, x = np.ogrid[-y_center:y_size - y_center, -x_center:x_size - x_center]
        print(x_center, x_size, x)
        center_mask = x ** 2 + y ** 2 <= (7.65 * self.scale_factor) ** 2
        self.image[:,:,:][~center_mask] = [0, 0, 0]


    def _read_lense_settings(self):
        pass

