# COVID-19-India_Data
## Data regarding region-wise spread of COVID-19 in India.

### Live Dashboard:
* These datasets have been beautifully visualized by **[@rahulrajpl](https://github.com/rahulrajpl)** on his **[dashboard]( http://randomwalk.in/covid19India/)**.

### Introduction:
* This repository stores datasets pertaining to the region-wise spread of COVID-19 in India.
* The data are arranged into two directories: *datasets* and *time-series*.
* I thank the **[MoHFW](https://www.mohfw.gov.in/)** and **[@covid19india](https://github.com/covid19india)** for providing a reliable source of raw data.
* I also thank each and every on-duty personnel on the frontlines of this battle against COVID-19. Let's help them by staying indoors.

### Functional Details:
* The *datasets* directory stores the daily updates in the CSV format.
* The *time-series* directory houses the CSV file storing the region-wise trends of the COVID-19 spread in India over time.
* The *update_scripts* directory contains the python scripts used for fetching data from their respective sources and updating the datasets accordingly.
* All the dates are represented in *'%d-%m-%Y'* format. Use the *dayfirst = True* argument of *pandas.read_csv()* function to correctly read the dates while loading the dataset into a dataframe.
* The *COVID19-fetch_India_regional_data.py* script scrapes the MoHFW webpage for updated data and generates/updates the corresponding files accordingly. I shall run this script daily to retrieve and record updates on the spread of COVID-19.
* The *COVID19-fetch_India_regional_historical_data.py* script extracts old historical data from the CovidCrowd repository on GitHub. This script was used once to load the old data that was no longer available on the MoHFW website.

### Sources:
* The primary source of these data is the home page of the **[Ministry of Health & Family Welfare](https://www.mohfw.gov.in/)**, Govt. of India. Daily updates are retrieved from this source since 28th March, 2020.
* Historical data before 28th March, 2020 have been extracted from the raw data available within the **[CovidCrowd](https://github.com/covid19india/CovidCrowd)** repository of [@covid19india](https://github.com/covid19india).
* The datasets housed in this repository are a mixture of data from these two sources and have been forged into a uniform format.

### Licensing:
This project is entirely from and for the public domain.  
Please feel free to utilise and distribute these datasets without any restrictions. (See MIT License)  

