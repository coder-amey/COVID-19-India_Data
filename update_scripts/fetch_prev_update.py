'''This script scrapes the home page of the MoHFW, Govt. of India, for updates on COVID-19 data and stores the latest tally in a CSV file with the corresponding date in the filename. It also updates the time-series dataset and regenerates the corresponding CSV file for the previous day's data.'''

import pandas as data
import numpy as maths
import os.path
from datetime import datetime

base_dir = os.path.join(os.path.dirname(__file__), "../")		#Obtain the path to the base directory for absosulte addressing.
date = datetime.strptime('05-05-2022', '%d-%m-%Y').strftime("%d-%m-%Y")		#Date of update.

#Tabulate the JSON data. Remove unwanted columns and rename the rest. Drop the final total.
updated_tally = data.read_json('https://www.mohfw.gov.in/data/datanew.json', orient = 'records')
updated_tally = updated_tally.drop(['sno', 'active', 'new_positive', 'new_cured', 'new_death', 'new_active', 'state_code'], axis = 1)
updated_tally = updated_tally.rename(columns = {"state_name": "Region", "positive": "Confirmed", "cured": "Recovered", "death": "Deceased"})
updated_tally = updated_tally[updated_tally.Region != ""]

#Reorder and format the columns.
updated_tally = updated_tally[["Region", "Confirmed", "Recovered", "Deceased"]]
updated_tally = updated_tally.astype({"Confirmed": int, "Recovered": int, "Deceased": int})
updated_tally = updated_tally.append(updated_tally.sum(numeric_only = True), ignore_index = True)
updated_tally.iloc[-1, 0] = "National Total"

#Correct the errors in the table.
#updated_tally.loc[updated_tally.Region == "Himanchal Pradesh", "Region"] = "Himachal Pradesh"

for region in [region for region in updated_tally.Region if '*' in region]:		#Remove the special annotations.
	updated_tally.loc[updated_tally.Region == region, "Region"] = ''.join(char for char in region if char != '*')	

#Store the dataset to a CSV file.
updated_tally.to_csv(base_dir + "datasets/India_aggregated_{}.csv".format(date), index = False)

#Insert a "Date" column to the data frame and merge it with the time-series.
updated_tally.insert(1, "Date", date)
time_series = data.read_csv(base_dir + "time-series/India_aggregated.csv")		#Load the time-series.
time_series = time_series[time_series["Date"] != date]	#Discard other updates made today.
time_series = data.concat([time_series, updated_tally])

#Rewrite the updated time-series to its CSV file.
time_series.to_csv(base_dir + "time-series/India_aggregated.csv", index = False)
