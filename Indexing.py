
### Missing: dealing with nans and inf, valueerrors, typeerrors
import numpy as np
import pandas as pd
from pathlib import Path

from pandas.core.frame import DataFrame

#Defenitions
n_samples_for_averging : int = 100
wights: tuple = (0.333, 0.333, 0.333)
data_path = Path(r"C:\Users\Anthony\Desktop\extra\Data.csv")


#####################################################################################


def read_data(data_path: Path) -> DataFrame:
    """ Pulling and reading the data into Dataframe.
    parm:
    return:
    """
    data_path = Path(data_path)
    row_data = pd.read_csv(data_path)
    return row_data


def process_samples(raw_data: DataFrame, n_samples: int = 10) -> DataFrame:
    """ averaging serval sampels in each column.
    param:
    returns:
    """
    time = raw_data["TIME"]
    ecg = raw_data["ECG"]
    breaths = raw_data["RESP"]
    gsr = raw_data["GSR"]

    processed_data = pd.DataFrame(columns=["time", "heart_rate", "breathing_rate", "gsr"])
    
    processed_data["time"] = time.iloc[0:-1:n_samples] #Not sure this is correct, the basic idea is marking each "time-frame" according to start-time
    processed_data["heart_rate"] = heart_rate(ecg, n_samples)
    processed_data["breathing_rate"] = breathing_rate(breaths, n_samples)
    processed_data["gsr"] = gsr.groupby(np.arange(len(gsr))//n_samples).mean()
    
    return processed_data

def heart_rate(ecg, n_samples):

def breathing_rate(breaths, n_samples):

def normalizing_values(avg_data: DataFrame, columns_list = ["ECG", "GSR", "RESP"]) -> DataFrame:
    """ normalazing each column.
    parm:
    return:
    """
    for column in columns_list:
        min = avg_data[column].min()
        max = avg_data[column].max()
        avg_data[column] = (avg_data[column] - min)/max
    normal_data = avg_data.copy()
    return normal_data


def index_adding(normal_data: DataFrame, wights: tuple = (0.333, 0.333, 0.333)) -> DataFrame:
    """ making an index according to wights.
    parm:
    return:
    """
    normal_data["Fear_Index"] = normal_data["ECG"]*wights[0] + normal_data["GSR"]*wights[1] +normal_data["RESP"]*wights[2]
    processed_data = normal_data.copy()
    return processed_data



if __name__ == "__main__":

    row_data = read_data(data_path)
    print("Row data\n",row_data) ######
    avg_data = averaging_samples(row_data, n_samples_for_averging)
    print("AVG data\n",avg_data) ######
    normal_data = normalizing_values(avg_data)
    print("Normal data\n", normal_data)
    processed_data = index_adding(normal_data, wights)
    print("Processed data\n",processed_data)



