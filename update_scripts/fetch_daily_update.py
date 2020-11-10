'''This script scrapes the home page of the MoHFW, Govt. of India, for updates on COVID-19 data and stores the latest tally in a CSV file with the corresponding date in the filename. It also updates the time-series dataset and regenerates the corresponding CSV file.'''

import pandas as data
import numpy as maths
import os.path
from datetime import datetime

base_dir = os.path.join(os.path.dirname(__file__), "../")		#Obtain the path to the base directory for absosulte addressing.
date = datetime.now().strftime("%d-%m-%Y") 	#Date of update.

#Tabulate the JSON data. Remove unwanted columns and rename the rest. Drop the final total.
updated_tally = data.read_json('https://www.mohfw.gov.in/data/datanew.json', orient = 'records')
updated_tally = updated_tally.drop(['sno', 'active', 'positive', 'cured', 'death', 'new_active', 'state_code'], axis = 1)
updated_tally = updated_tally.rename(columns = {"state_name": "Region", "new_positive": "Confirmed", "new_cured": "Recovered/Migrated", "new_death": "Deceased"})
updated_tally = updated_tally[updated_tally.Region != ""]

#Reorder and format the columns.
updated_tally = updated_tally[["Region", "Confirmed", "Recovered/Migrated", "Deceased"]]
updated_tally = updated_tally.astype({"Confirmed": int, "Recovered/Migrated": int, "Deceased": int})
updated_tally = updated_tally.append(updated_tally.sum(numeric_only = True), ignore_index = True)
updated_tally.iloc[-1, 0] = "National Total"

#Correct the errors in the table.
updated_tally.loc[updated_tally.Region == "Telengana", "Region"] = "Telangana"		#Correct the spelling of Telangana.
updated_tally.loc[updated_tally.Region == "Maharashtra***", "Region"] = "Maharashtra"		#Correct the entry for Maharashtra.
updated_tally = updated_tally[updated_tally.Region != "Lakshadweep"]			#Remove the empty record of Lakshadweep.

#Store the dataset to a CSV file.
updated_tally.to_csv(base_dir + "datasets/India_regional_aggregated_{}.csv".format(date), index = False)

#Insert a "Date" column to the data frame and merge it with the time-series.
updated_tally.insert(1, "Date", date)
time_series = data.read_csv(base_dir + "time-series/India_regional_aggregated.csv")		#Load the time-series.
time_series = time_series[time_series["Date"] != date]	#Discard other updates made today.
time_series = data.concat([time_series, updated_tally])

#Rewrite the updated time-series to its CSV file.
time_series.to_csv(base_dir + "time-series/India_regional_aggregated.csv", index = False)
