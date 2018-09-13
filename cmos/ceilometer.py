from . import Instrument
import datetime as dt
import csv


class Ceilometer(Instrument):
    """
    Class to read the ceilometer data to get the bottom cloud height.
    """

    def __init__(self, cloud_height_default=1000):
        self.instrument_name = self._check_for_instrument('ceilo')
        super().__init__()
        self.cloud_height = cloud_height_default

    def get_height(self, date):
        """
        Load data from Wettermast-ceilometer file. Look for CTWBU (lowest
        cloud base height). The data path needs to be set in the ceilo.ini.
        In the data path there should be the files in subdirectories.

        Args:
            date: datetime object

        Returns:
            cloud_height : Lowest cloud base height, if the file is broken
                a default value is returned

        """

        path = (self.path +
                str(dt.datetime.strftime(date, ('%Y%m')))+'/'+
                str(dt.datetime.strftime(date, ('%m%d')))+'.cl')

        try:
            with open(path) as csvfile:
                next(csvfile)
                readCSV = csv.reader(csvfile, delimiter=';')
                dates_off = []
                cloud_height = []

                for row in readCSV:
                    if row[15]:
                        cloud_height.append(float(row[15]))
                        date_str = row[0].lstrip().rstrip()+' '+row[1]+' +0000'
                        date_object = dt.datetime.strptime(date_str,
                                                           '%d.%m.%Y %H:%M:%S %z')
                        # calc date offset in utc
                        dates_off.append(abs(date_object
                                         -dt.timedelta(hours=self.tz_info_num)
                                         -date))


                self.cloud_height = cloud_height[dates_off.index(min(dates_off))]

                if self.cloud_height > 4000:
                    self.cloud_height = 1000

        except:
            print("Ceilometer file is broken...")

        return self.cloud_height