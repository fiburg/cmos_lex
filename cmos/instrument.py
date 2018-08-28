

class Instrument(object):

    def __init__(self):
        self.lat = None
        self.lon = None
        self.height = None

    def load_instrument_arguments(self,device):
        """
        This method is for reading a text file to set lat, lon, height, etc...

        Args:
            device:

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

        valid_instruments = ["hq","south","west","rad_south","rad_north"]

        if not instrument_name in valid_instruments:
            raise ValueError('%s is not a valid instrument_name.' % (instrument_name))