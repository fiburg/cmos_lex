

class Instrument(object):
    VALID_INSTRUMENT_NAMES = ["hq", "south", "west", "rad_south", "rad_north"]

    def __init__(self):
        self.lat = 53
        self.lon = 11
        self.height = 0
        self.date = None

    def load_instrument_arguments(self):
        """
        This method is for reading a text file to set lat, lon, height, etc...

        Args:
            instrument_name: Name of the instrument to use.

        Returns:

        """
        pass



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