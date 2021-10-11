import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def import_data(data,root=".",import_folder="clean_datasets"):
    def _import_on_time(dataset):
        DF = pd.read_csv(dataset,low_memory=False).drop(columns=["Unnamed: 0"])
        DF["Route"] = [tuple(l) for l in DF["Route"].str.replace("\(|\)|\'","",regex=True).str.split(", ")]
        DF["Scheduled Time"] = pd.to_datetime(DF["Scheduled Time"])
        return DF

    def _import_traffic_counts(dataset):
        DF = pd.read_csv(dataset).drop(columns="Unnamed: 0")
        DF["Timestamp"] = pd.to_datetime(DF["Timestamp"]) 
        return DF

    def _import_sites(dataset):
        return pd.read_csv(dataset)

    def _import_stops(dataset):
        return pd.read_csv(dataset).drop(columns="Unnamed: 0")

    def _import_lane_closure(dataset):
        DF = pd.read_csv(dataset).drop(columns="Unnamed: 0")
        DF["Boundaries"] = DF["Boundaries"].str.replace("\[|\]|\'","",regex=True).str.split(", ")
        DF["Direction"] = DF["Direction"].str.replace("\[|\]|\'","",regex=True).str.split(", ")
        DF["Date Closed - From"] = pd.to_datetime(DF["Date Closed - From"]) 
        DF["Date Closed - To"] = pd.to_datetime(DF["Date Closed - To"]) 
        DF["Geometry"] = [[[(float(l.replace("(","").split(", ")[0]),float(l.replace(")","").split(", ")[1])) for l in s.split("), (")] for s in m] 
                            for m in [j.replace("[[","").replace("]]","").split("], [") for j in DF["Geometry"].values]]
        return DF

    
    import_dict = {
        "ON_TIME":[f"{root}/{import_folder}/ON_TIME.csv",_import_on_time],
        "TRAFFIC_COUNTS":[f"{root}/{import_folder}/TRAFFIC_COUNTS.csv",_import_traffic_counts],
        "SITES":[f"{root}/{import_folder}/SITES.csv",_import_sites],
        "STOPS":[f"{root}/{import_folder}/STOPS.csv",_import_stops],
        "LANE_CLOSURE":[f"{import_folder}/LANE_CLOSURE.csv",_import_lane_closure],
        ## August 2021 data
        "ON_TIME_AUG_21":[f"{root}/{import_folder}/ON_TIME_AUG_21.csv",_import_on_time],
        "TRAFFIC_COUNTS_AUG_21":[f"{root}/{import_folder}/TRAFFIC_COUNTS_AUG_21.csv",_import_traffic_counts],
        "LANE_CLOSURE_AUG_21":[f"{root}/{import_folder}/LANE_CLOSURE_AUG_21.csv",_import_lane_closure],

    }
    dataset,import_func = import_dict[data]
    return import_func(dataset)