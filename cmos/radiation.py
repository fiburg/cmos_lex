from cmos import Instrument
import numpy as np
import datetime as dt
import csv


class Radiation(Instrument):

    def __init__(self, rad_position):
        self.instrument_name = self._check_for_instrument(rad_position)
        super().__init__()
        self.radiation = np.nan
        self.radiation_thres = np.nan

    def load_data_wxt(self,file):
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

    def _set_radiation_hq(self, date):
        path = (self.path + 'Tagesdateien/' +
                str(dt.datetime.strftime(date, ('%Y'))) + '/' +
                str(dt.datetime.strftime(date, ('%m'))) + '/' +
                str(dt.datetime.strftime(date, ('%d'))) + '/' +
                'MASTER.txt')

        try:
            with open(path) as csvfile:
                for _ in range(7):
                    next(csvfile)

                readCSV = csv.reader(csvfile, delimiter=';')
                dates_off = []
                radiation = []
                radiation_thres = []

                for row in readCSV:
                    radiation.append(float(row[18]))
                    if row[29]:
                        radiation_thres.append(float(row[29]))
                    else:
                        radiation_thres.append(np.nan)
                    
                    date_str = row[0] + ' ' + row[1] + ':00' + ' +0100'
                    date_object = dt.datetime.strptime(date_str,
                                                       '%d.%m.%Y %H:%M:%S %z')
                    
                    # calc date offset
                    dates_off.append(abs(date_object
                                         - dt.timedelta(hours=self.tz_info_num)
                                         - date))


                self.date = date
                self.radiation = radiation[dates_off.index(min(dates_off))]
                self.radiation_thres = radiation_thres[dates_off.index(min(dates_off))]

                if min(dates_off) > dt.timedelta(minutes=2):
                    self.radiation = np.nan
                    self.radiation_thres = np.nan

        except:
            print("Radiation file is broken...")

            self.radiation = np.nan
            self.radiation_thres = np.nan

    def is_shaded(self, date):
        self._set_radiation_hq(date)

        return (self.radiation < self.radiation_thres)

    def get_radiation(self, date):
        self._set_radiation_hq(date)

        return self.radiation

    def get_radiation_threshold(self, date):
        self._set_radiation_hq(date)

        return self.radiation

if __name__ == "__main__":
    rad_hq = Radiation('rad_hq')
    date_object = dt.datetime.strptime("30.08.2018 10:10:00 +0000",
                                       '%d.%m.%Y %H:%M:%S %z')

    print(rad_hq.is_shaded(date_object))