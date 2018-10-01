import matplotlib.pyplot as plt
import json
import numpy as np
from datetime import datetime as dt
from cmos.evaluation import *
import glob
from BCO.tools import tools
from matplotlib.dates import HourLocator, DateFormatter, DayLocator

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


class Statistics(object):

    def __init__(self,files):
        self.files = files
        self.cam = []
        self.pyr = []
        self.dates = []
        self.hss = []
        self.pss = []
        self.a = []
        self.b = []
        self.c = []
        self.d = []
        self.pyr_sun = []
        self.pyr_shadow = []
        self.cam_sun = []
        self.cam_shadow = []

        self.get_skill_scores()

    def get_skill_scores(self):


        for file in self.files:
            with open(file, "r") as f:
                data = json.loads(f.read())

            self.data = data
            dates = list(data.keys())
            pyr, cam = split_pyr_cam(data)

            cam[np.where(cam == 2)] = np.nan


            pyr[np.where(pyr == 2)] = np.nan

            pyr = pyr[~np.isnan(cam)]
            cam = cam[~np.isnan(cam)]
            pyr = pyr[~np.isnan(pyr)]
            cam = cam[~np.isnan(pyr)]

            cam[cam > 0.5] = 1
            cam[cam <= 0.5] = 0

            self.cam0 = cam
            a, b, c, d = get_contingency_table(cam, pyr)
            hss = heidke_skill_score(a, b, c, d)
            pss = peirce_skill_score(a, b, c, d)

            cam_sun, cam_shadow,pyr_sun, pyr_shadow = get_shades_vs_no_shades(cam,pyr)

            self.cam += cam.tolist()
            self.pyr += pyr.tolist()
            self.dates += dates
            self.hss.append(hss)
            self.pss.append(pss)
            self.a.append(a)
            self.b.append(b)
            self.c.append(c)
            self.d.append(d)
            self.pyr_sun.append(pyr_sun)
            self.pyr_shadow.append(pyr_shadow)
            self.cam_sun.append(cam_sun)
            self.cam_shadow.append(cam_shadow)

def plot_pie_chart(stat_class,name,format="pdf"):
    a = np.asarray(stat_class.a).sum()
    b = np.asarray(stat_class.b).sum()
    c = np.asarray(stat_class.c).sum()
    d = np.asarray(stat_class.d).sum()
    sizes = [a,b,c,d]
    # labels= ["Cam=W,Pyr=W","Cam=S,Pyr=W","Cam=W,Pyr=S","Cam=S,Pyr=S"]
    labels = ["Schattig richtig\nberechnet","Sonnig berechnet,\nobwohl schattig", "Schattig berechnet,\nobwohl sonnig", "Sonnig richtig\nberechnet"]

    colors = ["grey","silver","yellow","orange"]
    # explode = (0,0.1,0.1,0)

    fig,ax = plt.subplots()

    patches = ax.pie(sizes, shadow=False, colors=colors, radius=0.75)
    centre_circle = plt.Circle((0, 0), 0.5, color='black', fc='white', linewidth=0)
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    ax.axis("equal")
    # plt.tight_layout()
    plt.savefig("%s.%s"%(name,format),dpi=500)

def plot_skill_scores(South,West,name,format="pdf"):
    dates = [x for x in tools.daterange(dt(2018,8,28),dt(2018,9,3))]
    del dates[1]

    ls = "--"
    marker = "o"
    lw = 0.5
    ms = 2


    days = DayLocator()

    d_fmt = DateFormatter("\n%x")

    fig,ax = plt.subplots()
    ax.plot(dates, South.hss, ls=ls,lw=lw,marker=marker,ms=ms,color="b",label="Kamera Süd")
    ax.plot(dates,West.hss, ls=ls,lw=lw,marker=marker,ms=ms,color="r",label="Kamera West")
    ax.legend(loc="upper right")

    ax.set_ylabel("Heidke Skill Score")
    # ax.set_xlabel("Datum")
    ax.grid()

    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(d_fmt)

    plt.savefig("%s.%s" % (name, format))


if __name__ == "__main__":
    files_south = sorted(glob.glob("/home/tobias/Documents/cmos_data/results/SOUTH_HQ/statistic_results_*.json"))
    files_west = sorted(glob.glob("/home/tobias/Documents/cmos_data/results/WEST_HQ/statistic_results_*.json"))

    print(files_south)
    South = Statistics(files_south)
    West = Statistics(files_west)
    West.hss = West.hss[1:]

    plot_pie_chart(South,"south_pie")
    plot_pie_chart(West, "west_pie")

    # plot_skill_scores(South,West,"hss")