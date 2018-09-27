import cmos
from datetime import datetime as dt
import xarray as xr
import glob
import sys
from joblib import Parallel,delayed
import asyncio
import json


async def get_shades(file):
    print(file)

    sky_imager = cmos.SkyImager("hq")

    rad_hq = cmos.Radiation("rad_hq")
    ceilo = cmos.Ceilometer()
    sky_imager.get_date_from_image_name(file)
    cloud_height = ceilo.get_height(sky_imager.date)

    sky_imager.load_image(file,cloud_height=cloud_height)

    date_object = sky_imager.date

    pyr_is_shaded = float(rad_hq.is_shaded(date_object))
    cam_is_shaded = float(sky_imager.shadow_on_cam_position())

    result = {"pyr" : pyr_is_shaded,
              "cam" : cam_is_shaded}
    results[date_object.strftime("%Y%m%d_%H%M%S")] = result


def controller(files):
    tasks = [get_shades(file) for file in files]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))


def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def get_dates(files):
    date_strs = []
    for file in files:
        file = file.split("/")[-1]
        date_str = file.split("_")[-3:-1]
        date_str = "_".join(date_str)
        date_strs.append(date_str)

    return date_strs


def get_dummy_results(date_strs):
    for date_str in date_strs:
        results[date_str] = 777

if __name__ == "__main__":
    dates = ["20180827","20180828", "20180829", "20180830", "20180831","20180901","20180902","20180903"]
    for date in dates:
        files = sorted(glob.glob("/home/tobias/Documents/cmos_data/skyimager/%s/*.jpg"%date))
        global results
        results = {}
        out_file = "statistic_results_%s.json"%date
        #
        # strs = get_dates(files)
        # get_dummy_results(strs)

        file_parts = chunkIt(files,50)

        Parallel(n_jobs=1, verbose=5)(delayed(controller)(file) for file in file_parts)

        with open(out_file,"w") as f:
            f.write(json.dumps(results))

