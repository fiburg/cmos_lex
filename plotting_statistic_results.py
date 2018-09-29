import matplotlib.pyplot as plt
import json
import numpy as np
from datetime import datetime as dt
from cmos.evaluation import *

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
    file = "/home/tobias/PycharmProjects/MPI-GIT/cmos_lex/statistic_results_20180902.json"
    with open(file, "r") as f:
        data = json.loads(f.read())

    dates = list(data.keys())
    pyr, cam = split_pyr_cam(data)

    cam[np.where(cam == 2)] = np.nan
    cam[cam > 0.5] = 1
    cam[cam <=0.5] = 0

    pyr = pyr[~np.isnan(cam)]
    cam = cam[~np.isnan(cam)]
    diff = cam - pyr

    match = len(np.where(diff == 0)[0])
    non_match = len(np.where(diff != 0)[0])

    dates_dt = dates2datetime(dates)

    x = np.arange(0,len(pyr))

    plt.scatter(x,pyr, color="red")
    plt.scatter(x,cam, color="blue")
    plt.show()

    a,b,c,d = get_contingency_table(cam,pyr)
    hss = heidke_skill_score(a,b,c,d)
    pss = peirce_skill_score(a,b,c,d)

    print("RMSE : %f"%rmse(cam,pyr))
    print("MATCH: %i"%match)
    print("No MATCH: %i"%non_match)
    print("Heidke Skill Score: %f"%hss)
    print("Peirce Skill Score: %f"%pss)