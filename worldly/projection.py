""" Implements coordinate projections """

import math
from math import sin, cos, tan, acos, asin, sqrt, pi


class Projection(object):

    def __call__(self, *args):
        return self.project(*args)

    def project(self, lon, lat):
        return lon, lat


class SphericalMercator(Projection):

    def __init__(self, R):
        self.R = R

    def project(self, lon, lat):
        x = self.R / pi * (lon*pi/180.0 + pi)
        y = self.R / pi * (pi - math.log(tan(pi * (0.25 + lat/360))))
        return x, y


class SphericalStereographic(Projection):

    def __init__(self, k0, lon0, lat1):
        self.k0 = k0
        self.lon0 = lon0
        self.lat1 = lat1

    def project(self, lon, lat):
        lamda0 = self.lon0 * pi / 180.0
        phi1 = self.lat1   * pi / 180.0
        lamda = lon        * pi / 180.0
        phi = lat          * pi / 180.0
        k = 2 * self.k0 / (1 + sin(phi1)*sin(phi) +
                               cos(phi1)*cos(phi)*cos(lamda-lamda0))
        x = k * cos(phi) * sin(lamda-lamda0)
        y = k * (cos(phi1) * sin(phi) -
                 sin(phi1) * cos(phi) * cos(lamda-lamda0))
        return x, y


def sphere_distance(lon1, lat1, lon2, lat2, radius=1.0):
    dx = abs(lon1-lon2)
    dy = abs(lat1-lat2)

    if dx > 0.01 or dy > 0.01:      # use spherical law of cosines
        d_ = acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(dx))

    else:                           # use haversine
        d_ = (2 * asin(sqrt(sin(dy / 2.)**2 + cos(lat1) * cos(lat2) * sin(dx / 2.)**2)))

    return radius * d_


R = 6371000
WebMercator = SphericalMercator(128)
NorthPolarStereographic = SphericalStereographic(R, 0.0, 90.0)
SouthPolarStereographic = SphericalStereographic(R, 0.0, -90.0)

