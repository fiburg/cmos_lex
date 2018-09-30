from cmos import Instrument
import numpy as np
import datetime as dt
import csv
import glob

class Radiation(Instrument):

    def __init__(self, rad_position):
        self.instrument_name = self._check_for_instrument(rad_position)
        super().__init__()
        self.radiation = np.nan
        self.radiation_thres = np.nan

    def _get_radiation_mob(self, date):
        filenames = glob.glob(self.path + 'processed/*.txt')

        rad_hq = Radiation('rad_hq')
        rad_hq._get_radiation_hq(date)
        self.radiation_thres = rad_hq.get_radiation_threshold(date)

        dates_off = []
        radiation = []
        data_available = []

        for path in filenames:

            with open(path) as csvfile:
                for _ in range(1):
                    next(csvfile)

                readCSV = csv.reader(csvfile, delimiter=';')
                for row in readCSV:
                    #print(row[0]) # date
                    #print(row[1]) # hour
                    #print(row[4]) # lat
                    #print(row[5])  # lon
                    #print(row[13]) # sr
                    if(float(row[5]) <= self.lon+0.0005 and float(row[5]) >= self.lon-0.0005):
                        data_available.append(True)
                    else:
                        data_available.append(False)

                    radiation.append(float(row[13]))

                    date_str = row[0] + ' ' + row[1] + ' +0100'
                    date_object = dt.datetime.strptime(date_str,
                                                            '%d.%m.%Y %H:%M:%S %z')
                    dates_off.append(abs(date_object - date))

        self.date = date
        self.radiation = radiation[dates_off.index(min(dates_off))]

        if min(dates_off) > dt.timedelta(minutes=1) and data_available[dates_off.index(min(dates_off))]:
            print("... There is radiation data for "+self.instrument_name+
                  ", but the timedelta to your timestep exceeds one minute.")
            self.radiation = np.nan

        if not data_available[dates_off.index(min(dates_off))] or min(dates_off) > dt.timedelta(minutes=5):
            print("... There is no data available for the station "+
                self.instrument_name+" at this time")
            self.radiation = np.nan

    def _get_radiation_hq(self, date):
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
                    dates_off.append(abs(date_object - date))


                if(self.instrument_name == "rad_hq"):
                    self.date = date
                    self.radiation = radiation[dates_off.index(min(dates_off))]
                self.radiation_thres = radiation_thres[dates_off.index(min(dates_off))]

                if min(dates_off) > dt.timedelta(minutes=1):
                    if(self.instrument_name == "rad_hq"):
                        self.radiation = np.nan
                    self.radiation_thres = np.nan

        except FileNotFoundError as fnfe:
            raise fnfe

        except:
            print("Radiation file is broken...")

            self.radiation = np.nan
            self.radiation_thres = np.nan

    def is_shaded(self, date):
        if (self.instrument_name == "rad_hq"):
            self._get_radiation_hq(date)
        else:
            self._get_radiation_mob(date)

        if np.isnan(self.radiation):
            return np.nan

        if np.isnan(self.radiation_thres):
            return np.nan

        return (self.radiation < self.radiation_thres)

    def get_radiation(self, date):
        if (self.instrument_name == "rad_hq"):
            self._get_radiation_hq(date)
        else:
            self._get_radiation_mob(date)

        return self.radiation

    def get_radiation_threshold(self, date):
        if (self.instrument_name == "rad_hq"):
            self._get_radiation_hq(date)
        else:
            self._get_radiation_mob(date)

        return self.radiation_thres

if __name__ == "__main__":
    rad_hq = Radiation('rad_hq')
    date_object = dt.datetime.strptime("28.08.2018 15:10:00 +0000",
                                       '%d.%m.%Y %H:%M:%S %z')
    print(rad_hq.is_shaded(date_object))

    rad_north = Radiation('rad_north')
    print(rad_north.is_shaded(date_object))

    rad_south = Radiation('rad_south')
    print(rad_south.is_shaded(date_object))
