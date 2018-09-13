import cmos
import numpy as np
from . import Instrument
from datetime import datetime as dt


class Radiation(Instrument):

    def __init__(self,position):
        rad_position = "rad_" + position
        self.instrument_name = self._check_for_instrument(rad_position)
        # super().__init__()


    def load_data(self,file):
        # file = "C:/Users/darkl/Desktop/cmos/radiation/WXT_0A/201808/2800_0r4.txt"

        with open(file,"rb") as f:
            infos = np.genfromtxt(f,
                                  names=True,
                                  delimiter=";",
                                  dtype=None

                                  )

        def bytes2date(byte_array):
            """
            Helper function to convert the date and time columns from the input array
            to datetime objects.

            Args:
                byte_array: the raw array from the np.genfromtxt function

            Returns:
                array containing datetime.datetime objects
            """

            date_bytes = byte_array["DATE"]
            time_bytes = byte_array["TIME"]

            byte2str = lambda x: x.decode()
            byte2str = np.vectorize(byte2str)

            date_str_array = byte2str(date_bytes)
            time_str_array = byte2str(time_bytes)

            combine_date_time = lambda x, y: x + "_" + y
            combine_date_time = np.vectorize(combine_date_time)

            combined_str_array = combine_date_time(date_str_array,time_str_array)

            time_str2datetime = lambda x: dt.strptime(x.lstrip().rstrip(), "%d.%m.%Y_%H:%M:%S")
            time_str2datetime = np.vectorize(time_str2datetime)

            date_array = time_str2datetime(combined_str_array)

            return date_array

        data = {}
        data["date"] = bytes2date(infos)
        data["lat"] = infos["LAT"]
        data["lon"] = infos["LON"]
        data["radiation"] = infos["SR"]


        return data

    def rad2shadow(self):
        pass




