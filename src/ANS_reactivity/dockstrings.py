class OfflineAnalysisANS:
    """
    Base class for offline ANS measures' analysis objects.
    
    This class provides an "interface" for subclasses to implement which
    conforms with the larger data processing pipeline of this project.
    """

    def __init__(self, data_path: str = r"ANS-reactivity-during-VR-stimulation\Data.csv", sample_rate: int = 512, time_window: int = 10, weights: dict = {'ECG': 1/3, 'GSR': 1/3, 'RESP': 1/3}):

        if not (isinstance(data_path, Path) or isinstance(data_path, str)):
            raise TypeError(BAD_PATH_TYPE_MESSAGE.format(value=data_path))
        elif not Path(data_path).exists():
            raise ValueError(
                DIRECTORY_NOT_EXISTING_MESSAGE.format(value=data_path))
        else:
            self.data_path = data_path

        if not isinstance(sample_rate, int):
            raise TypeError(BAD_SAMPLE_RATE_TYPE_MESSAGE.format(value=sample_rate))
        else:
            self.sample_rate = sample_rate

        if not isinstance(time_window, int):
            raise TypeError(BAD_TIME_WINDOW_TYPE_MESSAGE.format(value=sample_rate))
        else:
            self.time_window = time_window

        if not isinstance(weights, dict):
            raise TypeError(BAD_WEIGHTS_TYPE_MESSAGE.format(value=weights))
        elif len(weights) != 3:
            raise ValueError(WEIGHTS_LENGTH_MESSAGE. format(value=weights))
        elif list(weights.keys()) != ["ECG", "GSR", "RESP"]:
            raise ValueError(BAD_KEYS_NAMES_MESSAGE.format(value=list(weights.keys())))
        elif not (isinstance(weights["ECG"], (int, float)) and isinstance(weights["GSR"], (int, float)) and isinstance(weights["RESP"], (int, float))):
            raise TypeError(WEIGHTS_ARE_NOT_NUMBERS_MESSAGE.format(value=weights))
        elif sum(weights.values()) != 1:
            raise ValueError(WEIGHTS_SUM_MESSAGE.format(value=sum(weights.values())))
        elif not (weights["ECG"] >= 0 and weights["GSR"] >= 0 and weights["RESP"] >= 0):
            raise ValueError(WEIGHTS_NEGATIVE_MESSAGE.format(value=weights))
        else:
            self.weights = weights

        self.n_samples = self.time_window*self.sample_rate

    def read_data(self) -> DataFrame:
        """ Pulling and reading the data into Dataframe.
        parm:
            self
        return:
            self.raw_data
        """
        self.raw_data = pd.read_csv(self.data_path)
        self.raw_data.columns = ["TIME", "ECG", "GSR", "RESP"]


    def change_weights(self, weights: dict = {'ECG': 1/3, 'GSR': 1/3, 'RESP': 1/3}):
        """
        This function enables to reconsider the wight of each parameter.
        parm:
            self
            weights - a dictionary of 3 keys, named "ECG", "GSR", "RESP". Each value must be a positive integer or float, that sum up to 1.
        """
        if not isinstance(weights, dict):
            raise TypeError(BAD_WEIGHTS_TYPE_MESSAGE.format(value=weights))
        elif len(weights) != 3:
            raise ValueError(WEIGHTS_LENGTH_MESSAGE. format(value=weights))
        elif list(weights.keys()) != ["ECG", "GSR", "RESP"]:
            raise ValueError(BAD_KEYS_NAMES_MESSAGE.format(value=list(weights.keys())))
        elif not (isinstance(weights["ECG"], (int, float)) and isinstance(weights["GSR"], (int, float)) and isinstance(weights["RESP"], (int, float))):
            raise TypeError(WEIGHTS_ARE_NOT_NUMBERS_MESSAGE.format(value=weights))
        elif sum(weights.values()) != 1:
            raise ValueError(WEIGHTS_SUM_MESSAGE.format(value=sum(weights.values())))
        elif not (weights["ECG"] >= 0 and weights["GSR"] >= 0 and weights["RESP"] >= 0):
            raise ValueError(WEIGHTS_NEGATIVE_MESSAGE.format(value=weights))
        else:
            self.weights = weights

    def heart_rate(self):
        '''
        This function extracts the heart rate from ECG data.
        Its output is a numpy array of beats per minute (bpm) for each time_window.
        Noisy ECG data that cannot produce a bpm output is ignored,
        and the previous time-window's bpm is refered to instead (unless the noise
        is in the first time window. In that case, the output of the bpm is NaN)
        param:
            self
        returns:
            heart_rate_for_every_chunk

        '''

        number_of_chunks = math.ceil((len(self.ecg))/self.n_samples)
        heart_rate_for_every_chunk = np.zeros(number_of_chunks)
        for data_chunks in range(number_of_chunks):
            try:
                start_of_chunk = data_chunks*self.n_samples
                if data_chunks != number_of_chunks:
                    end_of_chunk = (data_chunks+1)*self.n_samples
                else:
                    end_of_chunk = len(self.ecg)
                data_chunk = np.arange(start_of_chunk, end_of_chunk)
                relevant_data = self.ecg[data_chunk]
                relevant_data = relevant_data.reset_index(drop = True)

                working_data, measures = hp.process(relevant_data, self.sample_rate)
                bpm_measured = measures['bpm']
                if bpm_measured < 220:
                    heart_rate_for_every_chunk[data_chunks] = bpm_measured
                else:
                    raise Exception("")
            except:
                if data_chunks == 0:
                    heart_rate_for_every_chunk[data_chunks] = np.NaN
                else:
                    heart_rate_for_every_chunk[data_chunks] = heart_rate_for_every_chunk[data_chunks-1]

        return (heart_rate_for_every_chunk)

    def resp_rate(self) -> pd.DataFrame:
        """
        Extracts breathing rate from raw respiration data.
        param: 
            self
        returns:
            rsp_rate_avg - a Dataframe of momentary respiration rate averaged over appropriate time windows
        """
        rsp_cleaned = nk.rsp_clean(self.resp)
        rsp_rate = pd.DataFrame(nk.rsp_rate(rsp_cleaned, sampling_rate = self.sample_rate, window = self.time_window))
        rsp_rate_avg = rsp_rate.groupby(np.arange(len(rsp_rate))//self.n_samples).mean()
        return rsp_rate_avg

    def process_samples(self) -> DataFrame:
        """ This function collects all the processed data into one data frame.
        param:
            self
        returns:
            self.processed_data
        """
        self.time = self.raw_data["TIME"]
        self.ecg = self.raw_data["ECG"]
        self.resp = self.raw_data["RESP"]
        self.gsr = self.raw_data["GSR"]

        self.processed_data = pd.DataFrame(
            columns=["TIME", "ECG", "RESP", "GSR"])

        self.processed_data["TIME"] = self.time.iloc[0:-1:self.n_samples].reset_index(drop=True)
        self.processed_data["ECG"] = self.heart_rate()
        self.processed_data["RESP"] = self.resp_rate().reset_index(drop=True)
        self.processed_data["GSR"] = self.gsr.groupby(np.arange(len(self.gsr))//self.n_samples).mean().reset_index(drop=True)

    def normalizing_values(self, columns_list=["ECG", "GSR", "RESP"]) -> DataFrame:
        """ normalazing each column.
        parm: 
            self
            columns_list - a list of 3 strings, names of the normalized values
        return:
            self.normal_data
        """
        for column in columns_list:
            min = self.processed_data[column].min()
            max = self.processed_data[column].max()
            try:
                self.processed_data[column] = (self.processed_data[column]-min)/max
            except ZeroDivisionError:
                self.processed_data[column] = (self.processed_data[column]+1 -min)/max
            finally:
                self.normal_data = self.processed_data.copy()

    def score_adding(self):
        """ Making an index according to wights.
        parm:
            self
        return:
            self.scored_data
        """
        self.normal_data["Stress_Score"] = self.normal_data["ECG"]*self.weights["ECG"] + self.normal_data["GSR"]*self.weights["GSR"] + self.normal_data["RESP"]*self.weights["RESP"]
        self.scored_data = self.normal_data.copy()

    def plot_score(self):
        """ 
        This function plots the Stress Score calculated in each sample.
        The X axis displays the number of total samples, which depend on the time_window. 
        That means that the longer the time_window, the fewer there are samples.
        parm:
            self
        return:
            plot
        """
