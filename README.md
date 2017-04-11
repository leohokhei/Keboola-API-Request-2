# Keboola-API-Request-2
### Prepared by Leo Chan                                                                      ###
### Python Ver 2.7                                                                            ###
### Requirements:                                                                             ###
### API request and output into CSV                                                           ###

## Data Insight
### There are few locations raining or snowing all the time within the provided date range. It seems like most the locations are passing through the winter to spring phrase.

##Project Requirements
1. Get locations file
2. Gather daily weather stats for each location for a given date period (date_first and date_last fields)
3. Produce a single table which contains daily weather information for each location and each day (within individual data ranges)
4. Produce pivoted table as a quick precipitation report:
    a. X-axis: days (YYYY-MM-DD)
    b. Y-axis: locations (loc_id)
    c. Values: “precipProbability” in %
    d. NaNs are fine due to the variety of requested periods...
5. (Voluntary) - please provide any additional insight based on the data collected

##Steps Taken
1. Convert postal code to Longtitude and Latitude using Google API geocode
2. Get the dates within the given range
3. API request
    a. by id_loc
    b. by date
4. Extract precip(daily) in PERCENTAGE

##Files:
1. API.xlsx              >> contains all the darksky API and google's API
2. location.xlsx         >> list of locations with date and time that I am requesting
3. output.csv            >> daily weather output of every location within the time range
                         >> output is seperated with the location's postal code as sheetname
4. precipProbability     >> output of preciptation of each location within the time range in PERCENTAGE
5. run.py                >> SOURCE CODE

