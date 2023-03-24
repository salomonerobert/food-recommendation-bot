from typing import List
import math

def GetDistanceFromCoordinates(origin:List[float],target:List[float]):
    """
    uses the haversine formula to get the
    distance between two lat long coordinates
    in decimal degrees
    """
    #earth radius
    r= 6371000     
    lat1=math.radians(origin[0])
    lat2=math.radians(target[0])
    lon1=math.radians(origin[1])
    lon2=math.radians(target[1])
    a=math.sin((lat2-lat1)/2)
    b=math.cos(lat1)*math.cos(lat2)
    c=math.sin((lon2-lon1)/2)
    return 2*r*math.asin(math.sqrt(a*a+b*c*c))
#print(GetDistanceFromCoordinates([1.35644,103.83297],[1.35377165898043,103.834249377251]))

def GetCoordinatesFromStart(origin:List[float],distance:float,bearing:float):
    """
    Gets the coordinates of a point that is a certian distance
    from the origin with a given initial bearing clockwise from north
    """

    lat1=math.radians(origin[0])
    lon1=math.radians(origin[1])
    bearing=math.radians(bearing)
    r= 6371000  
    angularDist=distance/r
    lat = math.asin(math.sin(lat1)*math.cos(angularDist)+math.cos(lat1)*math.sin(angularDist)*math.cos(bearing))
    lon=lon1+math.atan2(math.sin(bearing)*math.sin(angularDist)*math.cos(lat1),math.cos(angularDist)-math.sin(lat1)*math.sin(lat))
    lat=math.degrees(lat)
    lon=math.degrees(lon)
    return (lat,lon)    