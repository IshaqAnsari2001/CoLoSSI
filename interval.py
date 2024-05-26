import socket
import os
import math
import sys
from optparse import OptionParser
import model_data as Data
import time

from simulator_interface import *

from dynamic import *

def get_time_unit():
    seconds  = getSimulationTime()
    TIME_UNIT = int(seconds/300)
    return TIME_UNIT

if __name__ == "__main__":
    usage = "usage: %prog [options] mdata"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()
    print(args, len(args))
    if len(args) not in [3]:
        print("Invalid number of arguments")
        sys.exit(0)
    


    # args[0] = INSTANCE NAME
    # args[1] = THRESHOLD VALUE
    # args[2] = meetup/nomeetup

    if args[2] == "meetup":
        unit = 150 
    else: 
        unit = 150
    initSimulatorInterface(16)   
    time.sleep(2) 
    while Task_status(100) == False:
        print("TIME UNIT IS  ",get_time_unit())
        #sendAdvanceSimTime(unit*2)
        #time.sleep(1.5)
        if get_time_unit() % int(args[1]) == 0:
            second = getSimulationTime()
            number,locations_accounted, groups_accounted, second, threshold, args[2], args[0], covs_accounted = information(args[0], args[1], args[2])
            second = getSimulationTime()
            call_UDP(number, locations_accounted, groups_accounted, second, threshold, args[2], args[0], covs_accounted)
            time.sleep(5)
            time_prev = get_time_unit()
            #sendAdvanceSimTime(150)
            time.sleep(2)
            sendAdvanceSimTime(300)
            time.sleep(2)
            for i in range(4):
                if get_time_unit == time_prev:
                    sendAdvanceSimTime(175)
            
        print(f" current time is {get_time_unit()} and the status is {Task_status(100)}")
        sendAdvanceSimTime(300)
        time.sleep(0.5)

    
    print("ALL TASKS COMPLETED IN :::: ",get_time_unit()," TIME UNITS")
    sys.exit()