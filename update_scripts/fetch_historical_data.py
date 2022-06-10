from datetime import datetime, timedelta
import json
import pandas as data
import os.path
import urllib.request

# [start, ..., cut_off)
start = datetime.strptime('02-06-2022', '%d-%m-%Y').date()	#Extract historical data from this date (inclusive).
cut_off = datetime.strptime('10-06-2022', '%d-%m-%Y').date()	#Extract historical data till this date (exclusive).
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
	df = data.DataFrame(data = rows, columns = ["Region", "Confirmed", "Recovered", "Deceased"])
	df = df.sort_values(by = "Region")
	df = df.append(df.sum(numeric_only = True), ignore_index = True)
	df.iloc[-1, 0] = "National Total"
	return(df)

increments = dict()		#Increments in cases per day bucketted over regions.

#Load historical data.
with urllib.request.urlopen("https://data.covid19bharat.org/v4/min/timeseries.min.json") as url:
	historical_data = json.loads(url.read().decode())

#Initialize the time-series.
time_series = data.DataFrame()

if __name__ == "__main__":
	#Transform the data into a date-wise tally.
	datewise_tally = dict()
	dates = [start +timedelta(days=x) for x in range((cut_off - start).days)]
	state_codes = {'AN': 'Andaman and Nicobar Islands', 'AP': 'Andhra Pradesh', 'AR': 'Arunachal Pradesh', 'AS': 'Assam',
						'BR': 'Bihar', 'CH': 'Chandigarh', 'CT': 'Chhattisgarh', 'DN': 'Dadra and Nagar Haveli and Daman and Diu',
						'DL': 'Delhi', 'GA': 'Goa', 'GJ': 'Gujarat', 'HR': 'Haryana', 'HP': 'Himachal Pradesh', 'JK': 'Jammu and Kashmir',
						'JH': 'Jharkhand', 'KA': 'Karnataka', 'KL': 'Kerala', 'LA': 'Ladakh', 'LD': 'Lakshadweep', 'MP': 'Madhya Pradesh',
						'MH': 'Maharashtra', 'MN': 'Manipur', 'ML': 'Meghalaya', 'MZ': 'Mizoram', 'NL': 'Nagaland', 'OR': 'Odisha',
						'PY': 'Puducherry', 'PB': 'Punjab', 'RJ': 'Rajasthan', 'SK': 'Sikkim', 'TN': 'Tamil Nadu', 'TG': 'Telangana', 'TR': 'Tripura',
						'UT': 'Uttarakhand', 'UP': 'Uttar Pradesh', 'WB': 'West Bengal'}

	#Generate date-wise records from the extracted data. Append them to the time-series.
	for date in dates:

		for state_code, state in state_codes.items():
			init_bucket(datewise_tally, date, state)
			record = historical_data[state_code]['dates'][date.strftime("%Y-%m-%d")]["total"]
			datewise_tally[date][state] = [record['confirmed'], record['recovered'], record['deceased']]
		daily_record = generate_dataset(datewise_tally[date])

		#Store the daily records as CSV files.
		daily_record.to_csv(base_dir + "datasets/India_aggregated_{}.csv".format(date.strftime('%d-%m-%Y')), index = False)

		#Add a date column and assimilate the records into a time_series dataframe with historical data.
		daily_record.insert(0, "Date", date.strftime('%d-%m-%Y'))
		time_series = time_series.append(daily_record, ignore_index = True)
	
	#Load the new time-series from its CSV file.
	time_series = data.concat([data.read_csv(base_dir + "time-series/India_aggregated.csv"), time_series], ignore_index = True)
	
	#Write the updated time-series to its CSV file.
	time_series.to_csv(base_dir + "time-series/India_aggregated.csv", index = False)
