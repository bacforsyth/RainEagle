#!/usr/bin/python
"""
    Read data from eagle and write to influxdb database
"""

__author__ = "Ben Forsyth"
__version__ = "0.1"

# import RainEagle
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from RainEagle import Eagle, to_epoch_1970

import argparse
import datetime
import dateutil
from influxdb import InfluxDBClient, SeriesHelper
from pprint import pprint
import time
import pytz

debug = 0

def create_parser():
    parser = argparse.ArgumentParser(
                    description="write data to influxdb")

    parser.add_argument("-a", "--address", dest="addr",
                    default=os.getenv('EAGLE_ADDR', None),
                    help="hostname or IP device")

    parser.add_argument("-p", "--port", dest="port", type=int,
                    default=os.getenv('EAGLE_PORT', 5002),
                    help="command socket port")

    parser.add_argument("-d", "--debug", dest="debug",
                    default=debug, action="count",
                    help="print debug info")

    parser.add_argument("-m", "--mac", dest="mac",
                    help="Eagle radio mac addrress")

    return parser

def write_demand_values(eagle, db):
    # get latest demand entry timestamp
    result = db.query("SELECT * FROM demand ORDER BY time DESC LIMIT 1")
    date = dateutil.parser.parse(list(result.get_points())[0]["time"])
    latest_demand_timestamp = (date - datetime.datetime(1970,1,1,0,0,0,0,pytz.UTC)).total_seconds()
    if debug:
        print "latest demand timestamp = %d" % latest_demand_timestamp

    data = eagle.get_historical_data(period="hour")
    points = []
    for (timestamp, value) in data:
        if timestamp <= latest_demand_timestamp:
            continue

        if debug:
            print "%i %f" % (timestamp, value)
        point = {"time": timestamp, "measurement": "demand", "fields": {"kW": value}}
        points.append(point)

    if debug:
        print points

    write_success = db.write_points(points, time_precision="s")
    if not write_success:
        #TODO: should probably raise exception
        print "failed to write data points"

def main():
    parser = create_parser()
    args = parser.parse_args()
    global debug
    debug = args.debug
    print args

    db = InfluxDBClient()
    databases = [x["name"] for x in db.get_list_database()]
    if "rain_eagle" in databases:
        eg = Eagle(**vars(args))
        db.switch_database("rain_eagle")
        write_demand_values(eg, db)
    else:
        print "Did not find database with name \"rain_eagle\""
        exit(-1)

    exit(0)

if __name__ == "__main__":
    main()
    exit(0)

