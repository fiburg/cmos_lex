import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import datetime
import numpy.ma as ma
import matplotlib as mpl

class Map(object):
    """
    Class to plot results on catropy map

    Attributes:
        extent : latitude min/max and longitude min/max
        request : image tile (eg. OpenStreetMap or GoogleMaps)
    """

    def __init__(self):
        #self.extent = [11.202, 11.265, 54.472, 54.51]
        self.extent = [11.15, 11.38, 54.43, 54.54]
        self.request = cimgt.OSM()  # OpenStreetMap

        self.date = None
        self.cloud_mask = None
        self.cloud_height = None
        self.sun_elevation = None
        self.sun_azimuth = None

    def load_cloud_mask(self, cloud_mask, cloud_height, date,
                        sun_azimuth, sun_elevation):
        """
        Load the cloud mask in the class

        Args:
            cloud_mask:
            cloud_height:
            sun_azimuth:
            sun_elevation:
        """

        self.cloud_mask = cloud_mask
        self.cloud_height = cloud_height
        self.date = date
        self.sun_azimuth = sun_azimuth
        self.sun_elevation = sun_elevation

    def make_map(self, projection=ccrs.PlateCarree()):
        """
        Make the map to plot

        Args:
            projection: catropy projection

        Returns:
            fig : matplotlib figure
            ax : matplotlib ax
        """

        fig, ax = plt.subplots(figsize=(8, 8),
                               subplot_kw=dict(projection=projection))
        # gl = ax.gridlines(draw_labels=True)
        # gl.xlabels_top = gl.ylabels_right = False
        return fig, ax

    def add_scale_bar(self,
                      ax, length=None, location=(0.75, 0.95), linewidth=3):
        """
        CITATION...
        ax is the axes to draw the scalebar on.
        length is the length of the scalebar in km.
        location is center of the scalebar in axis coordinates.
        (ie. 0.5 is the middle of the plot)
        linewidth is the thickness of the scalebar.
        """
        # Get the limits of the axis in lat long
        llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree())
        # Make tmc horizontally centred on the middle of the map,
        # vertically at scale bar location
        sbllx = (llx1 + llx0) / 2
        sblly = lly0 + (lly1 - lly0) * location[1]
        tmc = ccrs.TransverseMercator(sbllx, sblly)
        # Get the extent of the plotted area in coordinates in metres
        x0, x1, y0, y1 = ax.get_extent(tmc)
        # Turn the specified scalebar location into coordinates in metres
        sbx = x0 + (x1 - x0) * location[0]
        sby = y0 + (y1 - y0) * location[1]

        # Calculate a scale bar length if none has been given
        # (Theres probably a more pythonic way of rounding the number but this works)
        if not length:
            length = (x1 - x0) / 5000  # in km
            ndim = int(
                np.floor(np.log10(length)))  # number of digits in number
            length = round(length, -ndim)  # round to 1sf

            # Returns numbers starting with the list
            def scale_number(x):
                if str(x)[0] in ['1', '2', '5']:
                    return int(x)
                else:
                    return scale_number(x - 10 ** ndim)

            length = scale_number(length)

        # Generate the x coordinate for the ends of the scalebar
        bar_xs = [sbx - length * 500, sbx + length * 500]

        # Plot the scalebar label
        ax.text(sbx, sby, str(length) + ' km', size=14, transform=tmc,
                horizontalalignment='center', color='k',
                verticalalignment='bottom')

        # Plot the scalebar
        ax.plot(bar_xs, [sby, sby], transform=tmc, color='k',
                linewidth=linewidth)

    def plot_map(self, plot_path='../plot/map.png', tile_resolution=12):
        """
        Plot the map

        Args:
            plot_path: map path
            tile_resolution: resolution (max 19)
        """

        fig, ax = self.make_map(projection=self.request.crs)
        ax.set_extent(self.extent)
        ax.add_image(self.request, tile_resolution)
        self.add_scale_bar(ax, 5)
        cmap = plt.cm.Greys
        norm = mpl.colors.Normalize(vmin=0., vmax=1.)

        wk_data = [('HQ',
                    54.495071, 11.239483),
                   ('West', 54.493931, 11.225459),
                   ('Süd', 54.485390, 11.242269)]

        # Place a single marker point and a text annotation at each place.
        for name, lat, lon in wk_data:
            plt.plot(lon, lat, marker='x', markersize=9.0, markeredgewidth=2.5,
                     color='red',
                     transform=ccrs.PlateCarree())

            at_x, at_y = ax.projection.transform_point(lon, lat,
                                                       src_crs=ccrs.PlateCarree())


        self.cloud_mask[:, :, 2][np.isnan(self.cloud_mask[:, :, 2])] = 5
        self.cloud_mask[:, :, 1][np.isnan(self.cloud_mask[:, :, 1])] = 5
        self.cloud_mask[:, :, 0][self.cloud_mask[:, :, 0] == 0] = np.nan
        plt.contourf(self.cloud_mask[:, :, 2],
                   self.cloud_mask[:, :, 1],
                   self.cloud_mask[:, :, 0],
                   transform=ccrs.PlateCarree(),
                   cmap=cmap,
                   norm=norm,
                   alpha=0.6)

        plt.tight_layout()
        plt.savefig(plot_path)


if __name__ == "__main__":
    map = Map()
    lat = np.linspace(11.24, 11.25, 100)
    lon = np.linspace(54.49, 54.50, 100)

    #cloud, lat, lon
    cloud_mask = np.ones((100, 100, 3))

    lat = np.meshgrid(lat, lat)
    cloud_mask[:,:,2] = lat[0]

    lon = np.meshgrid(lon, lon)
    cloud_mask[:,:,1] = np.swapaxes(lon[0], 0, 1)

    #print(cloud_mask[:,:,1])

    map.load_cloud_mask(cloud_mask,
                        cloud_height=2840,
                        date=datetime.datetime(year=2018, month=8, day=26),
                        sun_azimuth=0,
                        sun_elevation=0)

    map.plot_map()