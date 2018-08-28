import os
import configparser

class Instrument(object):
    VALID_INSTRUMENT_NAMES = ["hq", "south", "west", "rad_south", "rad_north"]

    def __init__(self):
        self.lat = None
        self.lon = None
        self.height = None
        self.date = None

        self.load_instrument_arguments()

    def load_instrument_arguments(self):
        """
        This method is for reading a text file to set lat, lon, height, etc...

        Args:
            instrument_name: Name of the instrument to use.

        Returns:

        """



        here = os.path.realpath(__file__)
        here = os.path.split(here)[0]
        init_file = here + "/../data/cam%s.ini"%self._get_cam_number(self.instrument_name)

        print(init_file)

        with open(init_file):
            # This is to check weather the file exists.
            pass

        config = configparser.ConfigParser()
        config.read(init_file)

        self.lat = float(config["DEFAULT"]["LAT"])
        self.lon = float(config["DEFAULT"]["LON"])
        self.height = float(config["DEFAULT"]["HEIGHT"])



    @staticmethod
    def _get_cam_number(instrument_name):
        """
        Function to map the instrument names to the camera numbers.

        Args:
            instrument_name:

        Returns:

        """
        cams = {
            "hq":"2",
            "south":"4",
            "west":"3"
        }

        return cams[instrument_name]



    def _check_for_instrument(self, instrument_name):
        """
        Checks weather the instrument name is valid and raises an error if not.

        Args:
            instrument_name: Name of the instrument.

        Returns:

        """

        if not instrument_name in Instrument.VALID_INSTRUMENT_NAMES:
            raise ValueError('%s is not a valid instrument_name.\n Valid names are: %s' %
                             (instrument_name, "\n - ".join(self.VALID_INSTRUMENT_NAMES)))

        return instrument_name