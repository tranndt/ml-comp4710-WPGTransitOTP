import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json

API_KEY = "AIzaSyDPuM2hJqPTf3aAuwlhkE_LlblTa_bNP4w"

def import_data(data,root=".",import_folder="clean_datasets"):
    def _import_on_time(dataset):
        DF = pd.read_csv(dataset,low_memory=False).drop(columns=["Unnamed: 0"])
        DF["Route"] = [to_tuple(s,dtype=str,) for s in DF["Route"].str.replace("\'","").values]
        DF["Scheduled Time"] = pd.to_datetime(DF["Scheduled Time"])
        return DF

    def _import_traffic_counts(dataset):
        DF = pd.read_csv(dataset).drop(columns="Unnamed: 0")
        DF["Timestamp"] = pd.to_datetime(DF["Timestamp"]) 
        return DF

    def _import_lane_closure(dataset):
        DF = pd.read_csv(dataset).drop(columns="Unnamed: 0")
        DF["Boundaries"] = DF["Boundaries"].str.replace("\[|\]|\'","",regex=True).str.split(", ")
        DF["Direction"] = DF["Direction"].str.replace("\[|\]|\'","",regex=True).str.split(", ")
        DF["Date Closed - From"] = pd.to_datetime(DF["Date Closed - From"]) 
        DF["Date Closed - To"] = pd.to_datetime(DF["Date Closed - To"])
        DF["Time Closed - From"] = [pd.to_datetime(i).time() for i in DF["Time Closed - From"].values]
        DF["Time Closed - To"] = [pd.to_datetime(i).time() for i in DF["Time Closed - To"].values] 
        DF["Geometry"] = [[to_tuple_l(s) for s in m] for m in DF["Geometry"].str.split("\], \[").values]
        return DF

    def _import_road_network(dataset):
        DF = pd.read_csv(dataset).drop(columns="Unnamed: 0")
        DF.loc[:,"Location"] = np.array([to_tuple_l(s) for s in DF["Location"]],dtype=object)
        return DF

    def _import_sites(dataset):
        return pd.read_csv(dataset)

    def _import_stops(dataset):
        return pd.read_csv(dataset).drop(columns="Unnamed: 0")
    
    import_dict = {
        "ON_TIME":[f"{root}/{import_folder}/ON_TIME.csv",_import_on_time],
        "TRAFFIC_COUNTS":[f"{root}/{import_folder}/TRAFFIC_COUNTS.csv",_import_traffic_counts],
        "SITES":[f"{root}/{import_folder}/SITES.csv",_import_sites],
        "STOPS":[f"{root}/{import_folder}/STOPS.csv",_import_stops],
        "LANE_CLOSURE":[f"{import_folder}/LANE_CLOSURE.csv",_import_lane_closure],
        "ROAD_NETWORK":[f"{import_folder}/ROAD_NETWORK.csv",_import_road_network],
        ## August 2021 data
        "ON_TIME_AUG_21":[f"{root}/{import_folder}/ON_TIME_AUG_21.csv",_import_on_time],
        "TRAFFIC_COUNTS_AUG_21":[f"{root}/{import_folder}/TRAFFIC_COUNTS_AUG_21.csv",_import_traffic_counts],
        "LANE_CLOSURE_AUG_21":[f"{root}/{import_folder}/LANE_CLOSURE_AUG_21.csv",_import_lane_closure],
    }
    dataset,import_func = import_dict[data]
    return import_func(dataset)


def to_tuple(s,rev=False,dtype=float,strip="[(|)]",split=", ",):
    t = s.strip(strip).split(split)
    if rev: t = t[::-1]
    return tuple(map(dtype,t))

def to_tuple_l(s,rev=False,dtype=float,strip_l="[(|)]",split_l="), (",**kwargs):
    t = s.strip(strip_l).split(split_l)
    return [to_tuple(i,rev,dtype,**kwargs) for i in t]

# Python 3 program to calculate Distance Between Two Points on Earth, courtesy of https://www.geeksforgeeks.org/program-distance-two-points-earth/
from math import radians, cos, sin, asin, sqrt, acos, degrees
def distance(pt1,pt2):
    # Convert from degrees to radians.
    lat1 = radians(pt1[0])
    lon1 = radians(pt1[1])
    lat2 = radians(pt2[0])
    lon2 = radians(pt2[1])
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6378100
    # calculate the result
    return(c * r)

# Lon = x, Lat = y
# 1, (Latitude) On a longitude, as we consider average value of 1852 metres for a nautial mile, 1° of arc = 60*1852=111120 metres
# 2, On the Equator, 1° of longitude occupies: 1855.3248*60=111319.488 metres.
# On any other latitude, 1° of longitude occupies : 111319.488*cos(Latitude)
#https://www.distance.to/

def point_from(pt1,d,theta=0):
    # Convert from degrees to radians.
    lat1 = radians(pt1[0])
    lon1 = radians(pt1[1])
    LAT_METERS = 111120
    lat2 = lat1 + radians(d/LAT_METERS)*sin(radians(theta))

    LONG_METERS = 111319.488 * cos(lat1)
    lon2 = lon1 + radians(d/LONG_METERS)*cos(radians(theta))
    return (degrees(lat2),degrees(lon2))

point_within = lambda org,pt,d: distance(org,pt) <= d

def distance_within(org,pts,d=1000,key="index"):
    res = {"index":[],"value":[],"distance":[]}
    for i in range(len(pts)): 
        dist = distance(org,pts[i])
        if dist <= d:
            res["index"].append(i)
            res["value"].append(pts[i])
            res["distance"].append(dist)
    if key in res.keys():
        return res[key]
    else:
        return res


def fmt_timestamp(timestamp):
    return timestamp.hour+timestamp.minute/60

def getDrivingDistance(coord1: tuple[float, float], coord2: tuple[float, float], api_key: str=API_KEY if API_KEY in globals() else "") -> int:
    """
    Calculate driving distance between two coordinates using Google Map API.

    Parameters:
        - coord1: takes a geo coordinate in tuple
        - coord2: takes a geo coordinate in tuple
        - api_key: Google API key. It can be predefined as API_KEY global variable, or be overriden by provided key.

    Returns: 
        An int indicating the driving distance between two given coordinates.

    Depends on:
        requests, json
    """
    result_json = requests.request(method="GET", headers={}, data={}, 
    url=f"https://maps.googleapis.com/maps/api/directions/json?origin={coord1[0]},{coord1[1]}&destination={coord2[0]},{coord2[1]}&key={API_KEY}").text
    result_json = json.loads(result_json)
    return result_json["routes"][0]["legs"][0]["distance"]["value"]
