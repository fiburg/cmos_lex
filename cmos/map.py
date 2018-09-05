import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import datetime
import cmos
import collections

class Map(object):
    """
    Class to plot results on catropy map

    Attributes:
        extent : latitude min/max and longitude min/max
        request : image tile (eg. OpenStreetMap or GoogleMaps)
    """

    def __init__(self, lat_min=11.18, lat_max=11.32, lon_min=54.46, lon_max=54.53):
        self.extent = [lat_min, lat_max, lon_min, lon_max]
        self.request = cimgt.OSM()  # OpenStreetMap

        self.ax = None
        self.date = None
        self.cloud_height = None
        self.sun_azimuth = None
        self.sun_elevation = None
        self.max_elevation_angle = 30

        self.shadow_mask = None

    def set_positional_data(self, date, cloud_height,
                            sun_azimuth, sun_elevation):
        """
        Sets positional datas for current map.

        Args:
            date: datetime object of actual timestep
            cloud_height: cloud height for `date`
            sun_azimuth: azimuth of sun
            sun_elevation: elevation of sun
        """
        self.date = date
        self.cloud_height = cloud_height
        self.sun_azimuth = sun_azimuth
        self.sun_elevation = sun_elevation

    def _make_ax(self, subplot_info=111, projection=ccrs.PlateCarree()):
        """
        Creates the ax of the map

        Args:
            projection: catropy projection
        """

        self.ax = plt.subplot(subplot_info, projection=projection)

    def _add_scale_bar(self,
                      ax, length=None, location=(0.9, 0.05), linewidth=3):
        """
        Adds scale bar to the image.

        Args:
            ax : axes to draw the scalebar on.
            length : length of the scalebar in km
            location : center of the scalebar in axis coordinates.
                (ie. 0.5 is the middle of the plot)
            linewidth : thickness of the scalebar.
        """

        llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree())
        sbllx = (llx1 + llx0) / 2
        sblly = lly0 + (lly1 - lly0) * location[1]
        tmc = ccrs.TransverseMercator(sbllx, sblly)
        x0, x1, y0, y1 = ax.get_extent(tmc)
        sbx = x0 + (x1 - x0) * location[0]
        sby = y0 + (y1 - y0) * location[1]

        if not length:
            length = (x1 - x0) / 5000  # in km
            ndim = int(
                np.floor(np.log10(length)))  # number of digits in number
            length = round(length, -ndim)  # round to 1sf

            def scale_number(x):
                if str(x)[0] in ['1', '2', '5']:
                    return int(x)
                else:
                    return scale_number(x - 10 ** ndim)

            length = scale_number(length)

        bar_xs = [sbx - length * 500, sbx + length * 500]

        ax.text(sbx, sby, str(length) + ' km', size=14, transform=tmc,
                horizontalalignment='center', color='k',
                verticalalignment='bottom')

        ax.plot(bar_xs, [sby, sby], transform=tmc, color='k',
                linewidth=linewidth)

    def make_map(self, subplot_info=111, tile_resolution=12):
        """
        Adds the land map to the figure.

        Args:
            tile_resolution: resolution of map details (max=19)

        Returns:
            self to use it as ax
        """

        self._make_ax(subplot_info=subplot_info, projection=self.request.crs)
        self.ax.set_extent(self.extent)
        self.ax.add_image(self.request, tile_resolution)
        self._add_scale_bar(self.ax, 1)

        return self

    def add_clouds(self, cloud_mask, cmap="Greys", vmin=1., vmax=2.):
        """
        Add the cloud mask to the map.

        Args:
            cloud_mask: cloud mask 3dim array with cloud mask values,
                lats and lons
            cmap: string of desired colormap
            vmin: minimal value of cmap
            vmax: maximal value of cmap
        """

        cloud_mask[:, :, 0][cloud_mask[:, :, 0] == 0] = np.nan
        cloud = self.ax.contourf(cloud_mask[:, :, 2],
                     cloud_mask[:, :, 1],
                     cloud_mask[:, :, 0],
                     transform=ccrs.PlateCarree(),
                     cmap=cmap,
                     vmin=vmin,
                     vmax=vmax,
                     alpha=0.9)

    def add_outside_range(self,shadow_mask, cmap="Greys"):
        """
        Method to determine areas, which are outside of the range of the cameras.

        Args:
            shadow_mask:
            cmap:

        Returns:

        """
        outer_mask_size = 1000
        masking_value = 100

        outer_mask_lats = np.linspace(self.extent[0],self.extent[1],outer_mask_size)
        outer_mask_lons = np.linspace(self.extent[2],self.extent[3],outer_mask_size)
        outer_mask_values = np.linspace(masking_value,masking_value,outer_mask_size)

        lats_out, lons_out = np.meshgrid(outer_mask_lats, outer_mask_lons)

        outer_mask = np.zeros([1000,1000,3])
        outer_mask[:,:,0] = outer_mask_values
        outer_mask[:,:,1] = lons_out
        outer_mask[:,:,2] = lats_out

        self.outer_mask = outer_mask


        print("plotting mask!!!")

        outer = self.ax.contourf(outer_mask[:, :, 2],
                                 outer_mask[:, :, 1],
                                 outer_mask[:, :, 0],
                                 transform=ccrs.PlateCarree(),
                                 cmap=cmap,
                                 # vmin=vmin,
                                 # vmax=vmax,
                                 alpha=0.1
                                 )

    def create_shadow_mask(self,cloud_mask):
        """
        Uses the cloud mask to calculate the offset for the shadow on the ground.
        sets self.shadow_mask

        Args:
            cloud_mask:

        Returns:

        """
        cloud_mask[:, :, 0][cloud_mask[:, :, 0] == 0] = np.nan

        a = [cloud_mask[:, :, 0] == 2]
        b = [cloud_mask[:,:,1] == np.nan]

        mask = np.logical_and(a,b)[0,:,:]
        cloud_mask[: ,:, 0][mask] = np.nan
        cloud_mask[:, :, 1][mask] = np.nan
        cloud_mask[:, :, 2][mask] = np.nan

        # cloud_mask[:, :, 0][cloud_mask[:, :, 0] == 2] = np.nan


        shadow_mask = self.calculate_shadow_offset(cloud_mask)
        self.shadow_mask = shadow_mask

    def add_shadows(self, cmap="Greys_r", vmin=0., vmax=3.):
        """
        Adds the shadow mask to the map. The shadow mask is calculated
        by sun position and cloud mask.

        Args:
            cloud_mask: cloud mask 3dim array with cloud mask values,
                lats and lons
            cmap: string of desired colormap
            vmin: minimal value of cmap
            vmax: maximal value of cmap
        """

        if not isinstance(self.shadow_mask, collections.Iterable):
            raise ImportError("Shadow Mask is not created yet.")
        shadow_mask = self.shadow_mask

        a = [shadow_mask[:, :, 0] > 1][0]
        b = a.copy()
        b[:,:] = 0
        c = np.nan_to_num(shadow_mask[:,:,1])
        b = [c == 0][0]

        mask = np.logical_and(a,b)
        self.mask = mask
        shadow_mask[: ,:, 0][mask] = np.nan
        shadow_mask[:, :, 1][mask] = np.nan
        shadow_mask[:, :, 2][mask] = np.nan

        self.shadow_mask = shadow_mask


        shadow = self.ax.contourf(shadow_mask[:, :, 2],
                     shadow_mask[:, :, 1],
                     shadow_mask[:, :, 0],
                     transform=ccrs.PlateCarree(),
                     cmap=cmap,
                     vmin=vmin,
                     vmax=vmax,
                     alpha=0.5)

    def add_station_marker(self, name, lat, lon, color='red', marker='o', marker_size=14):
        """
        Adds the station marker (eg. for the sky imager at headquarter).

        Args:
            name : station name
            lat : latitude
            lon : longitude
            color : color
            marker : marker

        Returns:

        """

        self.ax.plot(lon, lat, marker=marker, markersize=marker_size, markeredgewidth=2.5,
                 color=color,
                 transform=ccrs.PlateCarree())

    def calculate_shadow_offset(self, cloud_mask):
        """
        Calculation of the shadow map - the projection of the cloud mask in
        relation to the sun position.

        Args:
            cloud_mask: cloud mask

        Returns:
            shadow_mask: shadow map
        """
        self.cloud_mask =cloud_mask
        dist = np.multiply(np.tan(np.deg2rad(self.sun_elevation)), self.cloud_height)

        dx = np.multiply(dist,
                         np.sin(np.deg2rad(self.sun_azimuth + 180)))  # +180 because of counter direction to sun azimuth
        dy = np.multiply(dist, np.cos(np.deg2rad(self.sun_azimuth+ 180)))  # dx, dy same units as R

        delta_longitude = np.divide(dx, (np.multiply(111320, np.cos(np.deg2rad(cloud_mask[:,:,1])))))  # dx, dy in meters
        delta_latitude = np.divide(dy, 110540)  # result in degrees long / lat

        final_longitude = np.add(cloud_mask[:,:,2], delta_longitude)
        final_latitude = np.add(cloud_mask[:,:,1], delta_latitude)

        shadow_mask = cloud_mask.copy()
        shadow_mask[:,:,1] = final_latitude
        shadow_mask[:,:,2] = final_longitude

        return shadow_mask

    def add_setting_title(self, text, size=14):
        """
        Sets title to map.

        Args:
            text: string
            size: font size
        """
        self.ax.set_title((text+' - '+self.date.strftime('%d.%m.%Y %H:%M:%S UTC')), size=size)

    def remove_sky_values(self):
        """
        Removes the clouds and shadows from the map, so you can plot
        the next values without downloading the background map again.
        """
        print("Plot: Removes sky values...")
        for coll in self.ax.collections:
            coll.remove()