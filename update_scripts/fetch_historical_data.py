import pandas as data
import os.path
from datetime import datetime

cut_off = datetime.strptime('28-03-2020', '%d-%m-%Y').date()	#Extract historical data till this date.
base_dir = os.path.join(os.path.dirname(__file__), "../")		#Obtain the path to the base directory for absosulte addressing.

def init_bucket(frame, date, region):
	'''Initialize a new bucket if it does not previously exist at frame[date][region].'''
	if(frame.get(date) == None):			#Partition does not exist. Create new.
		frame[date] = dict()

	if(frame[date].get(region) == None):		#Bucket does not exist. Create new.
		frame[date][region] = [0, 0, 0]

def generate_dataset(record):
	'''Generate a dataframe from an existing record.'''
	rows = [[region] + tally for region, tally in record.items()]
	df = data.DataFrame(data = rows, columns = ["Region", "Confirmed", "Recovered/Migrated", "Deceased"])
	df = df.sort_values(by = "Region")
	df = df.append(df.sum(numeric_only = True), ignore_index = True)
	df.iloc[-1, 0] = "National Total"
	return(df)

increments = dict()		#Increments in cases per day bucketted over regions.

#Load historical data.
patients_dataset = data.read_csv("https://raw.githubusercontent.com/covid19india/CovidCrowd/master/data/raw_data.csv", parse_dates = ['Date Announced', 'Status Change Date'], dayfirst = True)

#Initialize the time-series.
time_series = data.DataFrame()

if __name__ == "__main__":
	#Clean and transform the data.
	patients_dataset = patients_dataset[['Date Announced', 'Detected State', 'Current Status', 'Status Change Date']]
	patients_dataset = patients_dataset.rename(columns = {'Date Announced': 'Date', 'Detected State': 'Region', 'Current Status': 'Status', 'Status Change Date': 'Change_Date'})
	patients_dataset = patients_dataset.dropna(subset = ['Date', 'Region', 'Status'])

	#Generate a dictionary of date-wise recoded cases from the extracted data.
	for index, row in patients_dataset.iterrows():
		#Prepare values.
		date = row[0]
		region = row[1]
		status = row[2]
		change_date = row[3]
		init_bucket(increments, date, region)
	
		increments[date][region][0] += 1	#Increment confirmed cases.

		if(status != 'Hospitalized'):
			init_bucket(increments, change_date, region)
			if((status == 'Recovered') or (status == 'Migrated')):
				increments[change_date][region][1] += 1	#Increment recovered cases.
			else:
				increments[change_date][region][2] += 1	#Increment deceased cases.

	#Convert the list of daily increments into an aggregate tally.
	aggregate_sum = dict()
	for date, daily_increment in sorted(increments.items()):
		for region, new_cases in daily_increment.items():
			aggregate_sum[region] =[new_cases[i] + aggregate_sum.get(region, [0, 0, 0])[i] for i in range(3)]		#Add this day's respective new cases to the total cases so far.
		#Generate dataframe of daily records from the aggregate entries.
		daily_record = generate_dataset(aggregate_sum)
		#Store the daily records as CSV files.
		daily_record.to_csv(base_dir + "datasets/India_regional_aggregated_{}.csv".format(date.strftime('%d-%m-%Y')), index = False)
		if(date < cut_off):		#Do not process records after the cut-off date.
			#Add a date column and assimilate the records into a time_series dataframe with historical data.
			daily_record.insert(0, "Date", date.strftime('%d-%m-%Y'))	
			time_series = time_series.append(daily_record, ignore_index = True)	
	
	#Load the new time-series from its CSV file.
	time_series = data.concat([time_series, data.read_csv(base_dir + "time-series/India_regional_aggregated.csv")], ignore_index = True)
	
	#Write the updated time-series to its CSV file.
	time_series.to_csv(base_dir + "time-series/India_regional_aggregated.csv", index = False)
