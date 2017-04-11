#################################################################################################
### Keboola API Request 2                                                                     ###
### Prepared by Leo Chan                                                                      ###
### Python Ver 2.7                                                                            ###
### Requirements:                                                                             ###
### API request and output into CSV                                                           ###
#################################################################################################

### Steps Taken
### 1. Convert postal code to Longtitude and Latitude using Google API geocode
### 2. Get the dates within the given range
### 3. API request
###     a. by id_loc
###     b. by date
### 4. Extract precip(daily) in PERCENTAGE

import requests
import pandas as pd
import datetime
import json
import csv

dsky_api = '65decf1c72678739edfe7899ddb82bbf'

file1 = pd.ExcelFile('locations.xlsx')
readfile = pd.read_excel(file1, 'locations.csv',header=0)

###########################################################################################
### PARAMETERS                                                                          ###
###########################################################################################

### Searching for the min and max date for PRECIP table ###
### Prepare a list with the date range ###
### Lowest UNIX number = Min date; Highest UNIX number = Max date   ###
file_len = len(readfile)
date_min = int(readfile['date_first'][0])
date_min_count = 0
date_max = int(readfile['date_last'][0])
date_max_count = 0
date_range = []

#######################
### Finding Minimum ###
while (date_min_count < file_len):
    temp_date_min = int(readfile['date_first'][date_min_count])
    if (temp_date_min < date_min):
        date_min = temp_date_min
    date_min_count+=1
    
#######################
### Finding Maximum ###
while (date_max_count < file_len):
    temp_date_max = int(readfile['date_last'][date_max_count])
    if (temp_date_max > date_max):
        date_max = temp_date_max
    date_max_count+=1
    
##########################################################   
### create a list with all the dates within the range  ###
### Will be using this as the columns for precip table ###
date_min_1 = datetime.datetime.utcfromtimestamp(date_min)
date_max_1 = datetime.datetime.utcfromtimestamp(date_max)
days_diff = abs((date_max_1-date_min_1).days)
days_diff_count = 0
days_temp = date_min_1
while (days_diff_count < days_diff):
    date_range.append(str(days_temp.year)+"-"+str(days_temp.month)+"-"+str(days_temp.day))
    days_temp += datetime.timedelta(days=1)
    days_diff_count+=1
    
#########################################
### Create a list with all the loc_id ###
loc_count = 0
loc_id = []
while (loc_count < file_len):
    temp_loc = str(readfile['loc_id'][loc_count])
    loc_id.append(temp_loc)
    loc_count+=1
    
#################################
### DataFrame for PRECIP DATA ###
precip_data = pd.DataFrame(index = loc_id, columns = date_range)

################################################
### setting up column values = Daily Weather ###
t_column=['time','summary','icon','sunriseTime','sunsetTime','moonPhase','precipIntensity',
        'precipIntensityMax','precipIntensityMaxTime','precipProbability','precipType','precipAccumulation',
          'temperatureMin','temperatureMinTime','temperatureMax','temperatureMaxTime','apparentTemperatureMin',
       'apparentTemperatureMinTime','apparentTemperatureMax','apparentTemperatureMaxTime','dewPoint',
         'humidity','windSpeed','windBearing','visibility','cloudCover','pressure']

###############################################
### EXCEL writer for DAILY weather details ####
writer = pd.ExcelWriter('output.xlsx')


###########################################################################################
### Requesting data per LOCATION                                                        ###
###########################################################################################
request_count = 0
while (request_count < file_len):
    # Fetching the postal code    
    first = str(readfile['postal_code'][request_count])

    address = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+first)
    address_json = address.json()

    # Requesting lattitude, longitude and time for API request
    lat = str(address_json['results'][0]['geometry']['location']['lat'])
    lng = str(address_json['results'][0]['geometry']['location']['lng'])
    time = str(readfile['date_first'][request_count])
    
    #############################
    ### Request by Date first ###
    # convert unix to date time
    t1 = datetime.datetime.utcfromtimestamp(int(time))
    t2 = datetime.datetime.utcfromtimestamp(int(readfile['date_last'][request_count]))
    diff_days = abs((t2-t1).days)

    # A list with all the data for daily weather
    stuff = []
    stuff1 = pd.DataFrame(stuff, columns = t_column)

    temp_t = int(time)
    count = 0
    ####################################
    #### Fetching daily data by DAY ####
    while (count<diff_days):
        link = 'https://api.darksky.net/forecast/'+dsky_api+'/'+lat+","+lng+","+str(temp_t)+"?exclude=currently,flags,hourly"

        #############################################################
        ### Getting location daily weather                        ###
        #############################################################
        data = requests.get(link)
        data_json = json.loads(data.text)
        daily_data = data_json['daily']['data']

        time_t = datetime.datetime.utcfromtimestamp(int(temp_t))
        #t_list.append(str(time_t.year)+"-"+str(time_t.month)+"-"+str(time_t.day))

        ##insert data into stuff1 list
        daily_data1 = pd.DataFrame(daily_data, columns = t_column)
        stuff1=stuff1.append(daily_data1,ignore_index=True)

        #######################################################################
        ### Getting Precip data                                             ###
        ### if there is data, output the number into the precip_data table  ###
        #######################################################################
        current_time = str(time_t.year)+"-"+str(time_t.month)+"-"+str(time_t.day)
        precip = 0
        try:
            precip = float(daily_data[0]['precipProbability'])*100
            precip_data[current_time][str(readfile['loc_id'][request_count])] = precip
        ## if the table does not have values for precipProbability##
        except KeyError:
            ## no data means either it is raining or snowing ##
            precip_data[current_time][str(readfile['loc_id'][request_count])] = 100
        
        ## Next day if it is still within the range
        temp_t +=  86400
        count+=1

    ##############################################################################################
    ### Output Daily Weather tables to excel in multiple sheets with Postal Code as sheet name ###
    ##############################################################################################
    df = stuff1.set_index('time')
    df.to_excel(writer,str(readfile.postal_code[request_count]))
    
    ####################################
    ### Loop back to the next loc_id ###
    request_count+=1

writer.save()
#################################
#### Output Precip data in % ####
#################################
precip_data.to_csv('precipProbability.csv')
