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
from influxdb import InfluxDBClient
from pprint import pprint
import time

def write_demand_values(db):
    print "hi!"

def main():
    db = InfluxDBClient()
    databases = [x["name"] for x in db.get_list_database()]
    if "rain_eagle" in databases:
        write_demand_values(db)
    else:
        print "Did not find database with name \"rain_eagle\""
        exit(-1)

    exit(0)

if __name__ == "__main__":
    main()
    exit(0)

