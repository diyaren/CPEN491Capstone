import math


def cartesian(latitude, longitude, elevation=0):
    """Converts latitude and longitude pair and elevation above sea level the WGS84
    ellipsoid to equivalent cartesian coordinates.

    :param latitude latitude of point, in degrees
    :param longitude longitude of point, in degrees
    :param elevation meters above wgs84 sea level (wgs84 ellipsoid)
    """
    R = 6378137.0 + elevation  # earth radius in meters

    x = R * math.cos(math.radians(latitude)) * math.cos(math.radians(longitude))
    y = R * math.cos(math.radians(latitude)) * math.sin(math.radians(longitude))
    z = R * math.sin(math.radians(latitude))

    return (x, y, z)
