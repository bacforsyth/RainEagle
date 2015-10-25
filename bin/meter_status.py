#!/usr/bin/python
"""
    A simple script get current meter values
"""

__author__ = "Peter Shipley"
__version__ = "0.1.8"


# import RainEagle
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from RainEagle import Eagle, to_epoch_1970
import time
import argparse
from pprint import pprint

debug = 0

def create_parser():
    parser = argparse.ArgumentParser(
                    description="print power meter status")

    parser.add_argument("-a", "--address", dest="addr",
                    default=os.getenv('EAGLE_ADDR', None),
                    help="hostname or IP device")

    parser.add_argument("-p", "--port", dest="port", type=int,
                    default=os.getenv('EAGLE_PORT', 5002),
                    help="command socket port")

    parser.add_argument("--historical_data", dest="historical_data_period", choices=Eagle.historical_data_period_values(),
                    help="Print out historical data for the given period")

    parser.add_argument("-d", "--debug", dest="debug",
                    default=debug, action="count",
                    help="print debug info")

    parser.add_argument("-m", "--mac", dest="mac",
                    help="Eagle radio mac addrress")

    parser.add_argument("-t", "--timeout", dest="timeout",
                    help="Socket timeout")

    parser.add_argument("-v", '--version', action='version',
                    version="%(prog)s {0}".format(__version__) )

    return parser


def main() :

    parser = create_parser()
    args = parser.parse_args()
    print args
    eg = Eagle(**vars(args))
    # timeout=45,

    r = eg.get_device_data()

    print_instantdemand(r['InstantaneousDemand'])
    print

    print_currentsummation(r['CurrentSummation'])
    print

    if args.historical_data_period:
        print_historical_data(args.historical_data_period, eg.get_historical_data(period=args.historical_data_period))

    exit(0)


def twos_comp(val, bits=32):
    """compute the 2's compliment of int value val"""
    if( (val&(1<<(bits-1))) != 0 ):
        val = val - (1<<bits)
    return val


def print_currentsummation(cs) :

    multiplier = int(cs['Multiplier'], 16)
    divisor = int(cs['Divisor'], 16)
    delivered = int(cs['SummationDelivered'], 16)
    received = int(cs['SummationReceived'], 16)

    if multiplier == 0 :
        multiplier = 1

    if divisor == 0 :
        divisor = 1

    reading_received = received * multiplier / float (divisor)
    reading_delivered = delivered * multiplier / float (divisor)

    if 'TimeStamp' in cs :
        time_stamp = to_epoch_1970(cs['TimeStamp'])
        print "{0:s} : ".format(time.asctime(time.localtime(time_stamp)))
    print "\tReceived  = {0:10.3f} Kw".format(reading_received)
    print "\tDelivered = {0:10.3f} Kw".format(reading_delivered)
    print "\tMeter     = {0:10.3f} Kw".format( (reading_delivered - reading_received))


def print_instantdemand(idemand) :


    multiplier = int(idemand['Multiplier'], 16)
    divisor = int(idemand['Divisor'], 16)

#    demand = twos_comp(int(idemand['Demand'], 16))

    demand = int(idemand['Demand'], 16)

    if demand > 0x7FFFFFFF:
        demand -= 0x100000000

    if multiplier == 0 :
        multiplier = 1

    if divisor == 0 :
        divisor = 1

    reading = (demand * multiplier) / float (divisor)

    if 'TimeStamp' in idemand :
        time_stamp = to_epoch_1970(idemand['TimeStamp'])
        print "{0:s} : ".format(time.asctime(time.localtime(time_stamp)))

    print "\tDemand    = {0:{width}.3f} Kw".format(reading, width=10)
    print "\tAmps      = {0:{width}.3f}".format( ((reading * 1000) / 240), width=10)


def print_historical_data(period, data):
    print "Demand data for the past %s" % period
    for (timestamp, value) in data:
        timestamp_string = time.asctime(time.localtime(timestamp))
        print "%s, %f" % (timestamp_string, value)


#
if __name__ == "__main__":
    # import __main__
    # print(__main__.__file__)
    # print("syntax ok")
    main()
    exit(0)


