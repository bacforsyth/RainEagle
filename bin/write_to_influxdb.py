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
    class DemandSeriesHelper(SeriesHelper):
        # Meta class stores time series helper configuration.
        class Meta:
            client = db
            series_name = 'demand'
            fields = ['time', 'kW']
            tags = []
            bulk_size = 5
            autocommit = True
    print db
    print DemandSeriesHelper
    # TODO: get latest demand value to filter our data with
    data = eagle.get_historical_data(period="hour")
    for (timestamp, value) in data:
        # times are expected to be in 1970 epoch nanoseconds
        if debug:
            print "%i %f" % (timestamp, value)
        DemandSeriesHelper(time = timestamp * 1000000000, kW = value)

    DemandSeriesHelper.commit()

def main():
    parser = create_parser()
    args = parser.parse_args()
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

