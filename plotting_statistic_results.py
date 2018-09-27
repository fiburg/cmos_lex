import matplotlib.pyplot as plt
import json
import numpy as np
from datetime import datetime as dt

def split_pyr_cam(data):

    f = lambda x: (x["pyr"], x["cam"])
    f = np.vectorize(f)
    pyr, cam = f(list(data.values()))

    return pyr, cam

def dates2datetime(dates):

    f = lambda x: dt.strptime(x, "%Y%m%d_%H%M%S")
    f = np.vectorize(f)

    dates_obj = f(dates)
    return dates_obj

if __name__ == "__main__":
    file = "/home/tobias/PycharmProjects/MPI-GIT/cmos_lex/statistic_results_20180827.json"
    with open(file, "r") as f:
        data = json.loads(f.read())

    dates = list(data.keys())
    pyr, cam = split_pyr_cam(data)

    np.where(cam != 1)

    dates_dt = dates2datetime(dates)

    plt.plot(dates_dt,pyr, color="red")
    # plt.plot(dates_dt,cam, color="blue")
    plt.show()