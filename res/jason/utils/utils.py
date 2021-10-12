import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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