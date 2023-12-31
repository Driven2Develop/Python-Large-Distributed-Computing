"""
You are allowed use necessary python libraries.
You are not allowed to have any global function or variables.

Q4 T1

Find the busiest hour of the day for flights departing from "Hartsfield-Jackson Atlanta
International Airport" (ATL) in terms of the number of departures in November 2021.
"""
import math
import time
import threading
import pandas as pd
import os

class ThreadingSolution:
    """
    You are allowed to implement as many methods as you wish
    """
    def __init__(self, num_of_threads=None, dataset_path=None, dataset_size=None):
        self.num_of_threads = num_of_threads
        self.dataset_path = dataset_path
        self.dataset_size = dataset_size
        self.start_time = time.time()
        self.num_of_flight_by_hour = [0] * 24
        self.dataset_columns = ["FlightDate", "Airline", "Origin", "DepTime"] # only import the columns that are necessary 
    
    """
    Returns the tuple of computed result and time taken. eg., ("I am final Result", 3.455)
    """
    def run(self):
        print("Iymen Abdella | 40218280 | COMP 6231 FALL 2023 | Assignment 2: Parallel Programming | Q4 T1")
        threads = []
        lock = threading.Lock()

        # load csv and filter based on acceptance criteria
        print("{}s -- Loading csv file, and filtering based on acceptance criteria.".format(round(time.time() - self.start_time, 3)))
        df = pd.read_csv(self.dataset_path, usecols = self.dataset_columns)
        filtered_df = self.filter_csv(df)
        print("{}s -- Dataframe loaded.".format(round(time.time() - self.start_time, 3)))

        splits = self.get_splits(len(filtered_df), self.num_of_threads) # split the filtered dataframe into chunks for parallel processing

        # thread initialization loop
        for i in range(len(splits)-1):
            thread = threading.Thread(target=self.count_flights, args=(filtered_df, splits[i], splits[i+1], lock, i))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        # return max based on flight count
        max_hour = self.num_of_flight_by_hour.index(max(self.num_of_flight_by_hour))
        print("{}s -- The busiest hour at ATL airport during November 2021 is:\n{} with {} flights.".format(round(time.time() - self.start_time, 3), max_hour, max(self.num_of_flight_by_hour)))

        return max_hour, (time.time() - self.start_time)

    # helper method to filter out flights based on acceptance criteria reducing the counting effort
    def filter_csv(self, df):
        filter = ((pd.to_datetime(df["FlightDate"]).dt.year == 2021) & (pd.to_datetime(df["FlightDate"]).dt.month == 11) & (df["Origin"] == 'ATL'))  
        return df[filter]

    # helper method for splitting up the indexes of huge datasets depending on how many parallel mechanisms are needed
    def get_splits(self, size, num_of_splits):
        splits = []
        quotient, remainder = divmod(size, num_of_splits)
        splits = [quotient * i + min(i, remainder) for i in range(num_of_splits+1)]

        return [int(i) for i in splits] #return as a list of ints

    # counts flights and groups based on airline
    def count_flights(self, df, start_index, end_index, lock, thread_index):
        print("{}s -- Thread: {} -- Processing part of filtered CSV file from index {} to {}.\n".format(round(time.time() - self.start_time, 3), thread_index, start_index, end_index))

        num_of_flights = [0] *24

        for i in range(start_index, end_index): 
            row = df.iloc[i, :]
            
            if (math.isnan(row["DepTime"])): # skip if deptime is NaN
                continue

            num_of_flights[int(row["DepTime"]//100)] +=1
            
        lock.acquire()
        for i in range(len(self.num_of_flight_by_hour)):
            self.num_of_flight_by_hour[i] += num_of_flights[i]
        lock.release()

        print("{}s -- Thread: {} -- Processing finished, terminating thread.\n".format(round(time.time() - self.start_time, 3), thread_index))

if __name__ == '__main__':
    dataset_filename = "Combined_Flights_2021.csv"
    dataset_dir = "dataset"
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.path.join(dataset_dir, dataset_filename))
    dataset_size = len(pd.read_csv(dataset_path, usecols=["FlightDate"]))
    num_of_threads = 16

    print("{}s: Processing flights data of size {} with {} threads.".format(round(time.time(), 3), dataset_size, num_of_threads))
    solution = ThreadingSolution(num_of_threads=num_of_threads, dataset_path=dataset_path, dataset_size=dataset_size) #total should be about 6311871
    answer, timetaken = solution.run()
    print("The time it took to compute the solution was {} seconds. With {} threads.".format(round(timetaken, 3), num_of_threads))