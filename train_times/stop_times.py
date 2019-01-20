import urllib.request
import time
import os
import shutil
import zipfile
import io
from dotenv import load_dotenv
import csv
import sys
import calendar
import datetime

zip_file_name = "/gtfs_schedule_sydneytrains.zip"


def get_todays_station_times(data_dir):
    url = 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/sydneytrains'
    req = urllib.request.Request(url)

    try:
        api_key = os.getenv("TIMETABLE_API_KEY")
        req.add_header('Authorization', 'apikey ' + api_key)
    except TypeError:
        print("Error using saved api key, may not have been specified")

    file_name = data_dir + zip_file_name
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(req) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    with open(file_name, "rb") as f:
        z = zipfile.ZipFile(io.BytesIO(f.read()))
    
    z.extractall(path=data_dir)
    os.remove(file_name)
    date_of_analysis = datetime.date.today()
    day_of_analysis = str.lower(calendar.day_name[date_of_analysis.isoweekday() - 1])

    # create list of services that run on this day
    todays_services = []
    with open(data_dir + '/calendar.txt', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if row[day_of_analysis] == '1':
                start_date = datetime.datetime.strptime(row['start_date'], "%Y%m%d").date()
                end_date = datetime.datetime.strptime(row['end_date'], "%Y%m%d").date()
                if start_date <= date_of_analysis <= end_date:
                    todays_services.append(row['service_id'])
            line_count += 1

    todays_trips = []
    with open(data_dir + '/trips.txt', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if row['service_id'] in todays_services:
                todays_trips.append(row['trip_id'])
            line_count += 1


    station_name = os.getenv("STATION_NAME")

    stop_ids = []
    with open(data_dir + '/stops.txt', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if station_name in row['stop_name']:
                stop_ids.append(row['stop_id'])
            line_count += 1

    stops_at_station = []
    with open(data_dir + '/stop_times.txt', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if row['stop_id'] in stop_ids and row['trip_id'] in todays_trips:
                stops_at_station.append(row['departure_time'])
            line_count += 1

        print("stations stops: " + str(len(stops_at_station)))


if __name__ == "__main__":
    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    load_dotenv()
    destination_data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(destination_data_dir):
        os.makedirs(destination_data_dir)
    get_todays_station_times(destination_data_dir)
