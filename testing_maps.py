import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

fig = plt.figure(figsize=(10,20))  # predefined figure size, change to your liking.
# But doesn't matter if you save to any vector graphics format though (e.g. pdf)
ax = fig.add_axes([0.05,0.05,0.9,0.85])

# These coordinates form the bounding box of Germany
bot, top, left, right = 5.87, 15.04, 47.26, 55.06 # just to zoom in to only Germany
map = Basemap(projection='merc', resolution='f',
    llcrnrlat=54.411618176243145,
    llcrnrlon=10.985041886392082,
    urcrnrlat=54.509414708571114,
    urcrnrlon=11.362353592935051)
# map.readshapefile('./DEU_adm/DEU_adm1', 'adm_1', drawbounds=True)  # plots the state boundaries, read explanation below code
map.drawcoastlines()
map.drawcountries()
# map.fillcontinents(color='lightgray')
map.drawlsmask(land_color="grey", ocean_color="blue")
map.drawcounties()

plt.show()