from PIL import Image
import numpy as np
from . import Instrument

class SkyImager(Instrument):

    def __init__(self):

        self.image = None
        self.image_center_pixel = None


    def read_image(self,input_file, scale_factor):
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

