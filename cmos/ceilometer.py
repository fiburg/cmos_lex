from . import Instrument
from datetime import datetime as dt


class Ceilometer(Instrument):
    """
    Class to read the ceilometer data to get the bottom cloud height.
    """

    def __init__(self):
        super().__init__()
        self.instrument_name = self._check_for_instrument('ceilo')

    def load_data(self, date, path):
        """

        Args:
            date:
            path:

        Returns:

        """
        pass

    def get_height(self, date):
        pass