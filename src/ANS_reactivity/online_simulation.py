from offline_processing import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.core.frame import DataFrame
import pathlib as Path
import time

class OnlineAnalysisANS(OfflineAnalysisANS):
    """
        Child class for simulating online biofeedback system.
    
    This class simulates real-time reading of a csv file and enables creation of a bar chart that simulates a graphic
    change as a result of a change in stress measurement like biofeedback system and a line graph 
    that describes in real time the changing of the stress score that the program is calculating.
    """
    def __init__(self, data_path: Path = r"Data.csv" , sample_rate: int = 512, time_window: int = 10, weights: dict = {'ECG': 1/3, 'GSR': 1/3, 'RESP': 1/3}):
        """init method receives initial values and creates values to create the graphs 
            Input:  
                data_path: Path - path to stress measurements data 
                sample_rate: int - measurements werte sampled with these sample rates
                time_window: int - time in which a chunk of measurements was processed
                weights: dict - weights that are given to each measurement that create the general stress score
            Output:
            None
                 
        """
        OfflineAnalysisANS.__init__(self, data_path, sample_rate, time_window,  weights)
        #Bar data
        self.bar_colors = ["r", "k", "g", "b"]
        self.x_positions = [0., 0.5, 1.0, 1.5]
        self.width = 0.15
        #Graph data
        self.graph_width = 20
        self.graph_x = np.linspace(start = 0, stop = self.graph_width, num= self.graph_width)
        self.graph_y = np.linspace(start = 0, stop = self.graph_width, num= self.graph_width)

    def compute_data_for_simulation(self):
        """  This method creates a chain of processing the raw data into the final Dataframe with stress scores
            Input:  
            None
            Output:
            None       
        """
        self.read_data()
        self.process_samples()
        self.normalizing_values()
        self.score_adding()

        
    def plot_me(self, labels: list = ["ECG", "GSR", "RESP", "Stress_Score"], fear_values = [0.5, 0.5, 0.5, 0.5]):
        """ This generator is a tool for creating and recreating the real-time updating bar chart  
            Input:  
            labels: list - the labels under each bar
            fear_values : list - the initial values for each bar (0.5)
            Output:
            Yield : fig: matplotlib.figure.Figure -   figure object
                    ax: matplotlib.axes._subplots.AxesSubplot - axis object            
        """
        plt.ion()
        fig, ax = plt.subplots()
        rects1 = ax.bar(self.x_positions, fear_values, self.width, label='Stress_Score', color = self.bar_colors)
        ax.bar_label(rects1)
        while True:
            ax.set_ylabel('Stress_Score')
            ax.set_title('Real time Data')
            ax.set_xticks(self.x_positions)
            ax.set_xticklabels(labels)
            ax.set_ylim([0, 1.2])
            yield fig, ax

    def update_data_simulation(self, ax, i):
        """  This method simulates reading of real-time data reading one row at a time in the Dataframe
            Input:  
            ax: matplotlib.axes._subplots.AxesSubplot - axis object
            i: index
            Output:
            rects1 :matplotlib.container.BarContainer -Structure of the bar chart 
        """
        real_time_data = self.scored_data.iloc[i, :]
        fear_values = [real_time_data["ECG"], real_time_data["GSR"], real_time_data["RESP"], real_time_data["Stress_Score"]]
        rects1 = ax.bar(self.x_positions, fear_values, self.width, label='Stress_Score', color = self.bar_colors)
        return rects1

    def bar_simulation(self, loop_time: float = 0.1):
        """  This method creates a chain of additional methods in order to simulate a real-time updating
            barchart. The barchart simulates real-time reading and processing of measurements and presents
            them with graphics changing in a similar way to biofeedback systems. 
            Input:  
            loop_time: float - the time between each reading of the data
            Output:
            None      
        """
        self.compute_data_for_simulation()
        gen_plot = self.plot_me()
        fig, ax = next(gen_plot)

        for i in range(len(self.scored_data.index)):
            plt.cla()
            rects1 = self.update_data_simulation(ax, i)
            next(gen_plot)
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(loop_time)

    def plot_me_gragh(self):
        """ This generator is a tool for creating and recreating the real-time updating line graph  
            Input:
            None  
            Output:
            Yield : fig: matplotlib.figure.Figure -   figure object
                     line1: matplotlib.lines.Line2D - line structure
              
        """
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 8))
        line1, = ax.plot(self.graph_x, self.graph_y)
        ax.set_ylim([0, 1.2])
        plt.title("Real Time Data", fontsize=20)
        plt.xlabel("Sampels")
        plt.ylabel("Stress_Score")
        yield  line1, fig
        while True:
            line1, = ax.plot(self.graph_x, self.graph_y)
            ax.set_ylim([0, 1.2])
            plt.title("Real Time Data", fontsize=20)
            plt.xlabel("Sampels")
            plt.ylabel("Stress")
            print(type(fig))
            print(type(line1))
            yield line1, fig

    def update_data_simulation_graph(self, i):
        """ This method simulates reading of real-time data reading one row at a time in the Dataframe
            Creating values for the x and y axes
            Input:  
            i: index
            Output:
            None
        """
        self.graph_y = self.graph_y.tolist()
        self.graph_x = self.graph_x.tolist()
        self.graph_y.append(self.scored_data["Stress_Score"].iloc[i])
        self.graph_x.append(i)

        while len(self.graph_y) > self.graph_width:
            self.graph_y.pop(0)
            self.graph_x.pop(0)
        self.graph_y = np.array(self.graph_y)
        self.graph_x = np.array(self.graph_x)

    def gragh_simulation(self, loop_time: float = 0.1):
        """ This method creates a chain of additional methods in order to simulate a real-time updating
            line graph. The line graph simulates a real-time presentation of the stress scores of the subject 
            throughout the experiment.
            Input:  
            loop_time: float - the time between each reading of the data
            Output:
            None      
        """
        self.compute_data_for_simulation()
        gen_plot = self.plot_me_gragh()
        line1, fig= next(gen_plot)
        for i in range(len(self.scored_data.index)):
            plt.cla()
            self.update_data_simulation_graph(i)
            line1, fig = next(gen_plot)
            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(loop_time)




if __name__ == "__main__":
    on_val = OnlineAnalysisANS()
    on_val.bar_simulation()
    on_val.gragh_simulation()