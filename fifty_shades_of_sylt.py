import cmos
from datetime import datetime as dt
import xarray as xr
import glob
import sys
from joblib import Parallel,delayed
import asyncio
import json
import numpy as np
import ast


async def get_shades(file):
    print(file)
    results = {}
    sky_imager = cmos.SkyImager("south")

    rad_hq = cmos.Radiation("rad_hq")
    ceilo = cmos.Ceilometer()
    sky_imager.get_date_from_image_name(file)
    cloud_height = ceilo.get_height(sky_imager.date)

    sky_imager.load_image(file,cloud_height=cloud_height)

    date_object = sky_imager.date

    hq_lat = 54.494541
    hq_lon =  11.240319

    pyr_is_shaded = float(rad_hq.is_shaded(date_object))

    cam_is_shaded = sky_imager.shadow_on_lat_lon(hq_lat,hq_lon)
 #   print("RESULT: %f"%cam_is_shaded)

    result = {"pyr" : pyr_is_shaded,
              "cam" : cam_is_shaded}
    results[date_object.strftime("%Y%m%d_%H%M%S")] = result
    return results

def controller(files):
    tasks = [get_shades(file) for file in files]
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(asyncio.wait(tasks))
    return str(res)

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

def Parrallel2results(stuff):
    results = {}
    for element in stuff:
        result_parts = element.split("result=")[1:]
        for result_part in result_parts:
            second_part = result_part.split(">")[0]
            second_part_json = second_part.replace("'",'"')
            temp_r = json.loads(second_part_json)
            results[list(temp_r.keys())[0]] = list(temp_r.values())[0]

    return results




if __name__ == "__main__":
    dates = [ "20180830", "20180831","20180901","20180902","20180903","20180827","20180828"]
    for date in dates[1:]:
        files = sorted(glob.glob("/home/tobias/Documents/cmos_data/skyimager/WKM4/%s/*.jpg"%date))
        # print(files)

        out_file = "statistic_results_%s.json"%date


        chunk_numbers = 40
        file_parts = chunkIt(files,chunk_numbers)

        stuff = Parallel(n_jobs=-1, verbose=5)(delayed(controller)(file) for file in file_parts)
        try:
            results = Parrallel2results(stuff)

            with open(out_file,"w") as f:
                f.write(json.dumps(results))
        except:
            print("NO OUTPUTFILE WRITTEN! For Date: %s"%date)
            break

