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
from influxdb import InfluxDBClient, SeriesHelper
from pprint import pprint
import time

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
    # TODO: get latest demand value to filter our data with
    data = eagle.get_historical_data(period="hour")
    points = []
    for (timestamp, value) in data:
        # times are expected to be in 1970 epoch nanoseconds
        if debug:
            print "%i %f" % (timestamp, value)
        point = {"time": timestamp, "measurement": "demand", "fields": {"kW": value}}
        points.append(point)

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

