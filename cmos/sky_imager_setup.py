from . import Instrument


class SkyImagerSetup(Instrument):
    """
    Class for creating the configuration file for each camera.
    This class only needs to be called once for each camera, as the position
    of the cameras should not change over the project.

    """

    def __init__(self,instrument_name):
        pass


