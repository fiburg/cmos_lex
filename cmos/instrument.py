import os
import configparser


class Instrument(object):
    """
    Abstract class for each instrument. Valid instruments are the sky imagers `hq`, `south`, `west`, the mobile
    radiation stations `rad_south`, `rad_north` and the ceilometer `ceilo`.

    Attributes:
        lat : Latitude
        lon : Longitude
        height : Height of the instrument
        date : timestamp, datetime object
    """

    VALID_INSTRUMENT_NAMES = ["hq", "south", "west", "rad_south", "rad_north", "rad_hq", "ceilo"]

    def __init__(self):
        self.lat = None
        self.lon = None
        self.height = None
        self.date = None
        self.tz_info_num = None
        self.azimuth_offset = None
        self.load_instrument_arguments()

    def load_instrument_arguments(self):
        """
        This method is for reading a text file to set lat, lon, height, etc...

        Args:
            instrument_name: Name of the instrument to use.
        """

        here = os.path.realpath(__file__)
        here = os.path.split(here)[0]
        init_file = (here+"/../data/"+self._get_inst_inits(self.instrument_name)+".ini")

        # print(init_file)

        with open(init_file):
            # This is to check weather the file exists.
            pass

        config = configparser.ConfigParser()
        config.read(init_file)

        self.lat = float(config["DEFAULT"]["LAT"])
        self.lon = float(config["DEFAULT"]["LON"])
        self.height = float(config["DEFAULT"]["HEIGHT"])
        self.tz_info_num = float(config["DEFAULT"]["UTCOFFSET"])
        self.path = str(config["DEFAULT"]["PATH"])
        self.azimuth_offset = float(config["SPECIFIC"]["AZIMUTHOFFSET"])

    @staticmethod
    def _get_inst_inits(instrument_name):
        """
        Function to map the instrument names to the init files.

        Args:
            instrument_name:

        Returns:

        """
        inst = {
            "hq":"cam2",
            "south":"cam4",
            "west":"cam3",
            "ceilo":"ceilo",
            "rad_hq":"rad_hq",
            "rad_north": "rad_north",
            "rad_south": "rad_south"
        }

        return inst[instrument_name]



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