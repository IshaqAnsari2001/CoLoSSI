import socket
import os
import math
import sys
from optparse import OptionParser
import model_data as Data
import time

from simulator_interface import *
from interval import *


def get_num_agents(string):
    args = string.split("_")
    for elem in args:
        if "n" in elem:
            unit = elem
            unit = unit.split("t")
            unit = unit[0][1:]
    return unit

def get_num_tasks(string):

    args = string.split("_")
    count = 0 

    for elem in args:
        if "-" in elem and count == 0:
            el = elem.split("-")
            num = int(el[0][1:])
            count = 1

    numberOfTasks = (num*num)
    return numberOfTasks

def Task_status(numberOfTasks):
    global_dict = {}
    status = [False] * numberOfTasks
    global_dict = getGlobalCoverage()
    count = 0 
    print('\n',global_dict)
    for k in global_dict:
        if global_dict[k] <= 0.05 and global_dict[k] >= 0:
            status[int(k)] = True
            count += 1
    #print(status,'\n')
    if count == status.count(True):
        print("\tTask Completed till now ::: ", count)
        print("\tTask Left till now ::: ", numberOfTasks - count)
    print("\nTASK COMPLETION STATUS :::: ", end = " ")
    if count == numberOfTasks and status.count(True) == numberOfTasks:
        return True
    else:
        return False

def information(args0, args1, args2):
    '''
    usage = "usage: %prog [options] mdata"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()
    print(args, len(args))
    if len(args) not in [3]:
        print("Invalid number of arguments")
        sys.exit(0)

    # args[0] == INSTANCE NAME
    # args[1] == THRESHOLD
    # args[2] == meetup/nomeetup
    '''
    threshold = str(args1)
    groups_dict = {}
    numberOfTasks = get_num_tasks(args0)
    numberOfAgents = get_num_agents(args0)
    '''
    initSimulatorInterface(int(numberOfAgents))
    time.sleep(2)
    '''

    covmaps, neighbours, locs = getInfo(int(numberOfAgents))
    # print info
    dictionary = {}
    locations = {}
    coverage = {}
    for i in locs.keys():
        #print("===== Agent {} ======".format(i))
        #print("Current Location: {}".format(locs[i]))
        locations[i] = locs[i]
        #print("Current Neighbours: ", end="")
        array = []
        for (n,t) in neighbours[i].items():
            #print("Agent {} lastTimeSeen {}".format(n,t), end=" ")
            array.append("Agent {} lastTimeSeen {}".format(n,t).split(" "))
            #print("")
        #print(covmaps)
        #for keys in covmaps:
        #    print("Coverage for Agent ", keys, covmaps[keys],'\n')
        dictionary[i] = array  

    

    for keys in dictionary:
        for i in range(len(dictionary[keys])):
            old = int(dictionary[keys][i][1])
            dictionary[keys][i][1] = old
            olds = int(dictionary[keys][i][-1])
            dictionary[keys][i][-1] = olds
        print("Agent ",keys," ::: ",dictionary[keys],'\n')
    seconds = []
    for keys in dictionary:
        for i in range(len(dictionary[keys])):
            if dictionary[keys][i][-1] not in seconds:
                seconds.append(dictionary[keys][i][-1])
    
    
    second = getSimulationTime()  
    time.sleep(1)
    Current_time = int(second - 20)
    print("SECONDS :::: ",second,"  CURRENT TIME :::: ", Current_time,"   DIFFERENCE ::: ", second - Current_time)
    for keys in dictionary:
        garray = []
        #print("Agent ",keys," :::: ", end = " ")
        for index in range(len(dictionary[keys])):
            temp_key = (dictionary[keys][index][1])
            temp_val = dictionary[keys][index][-1]
            #print(type(temp_key))
            if temp_key != 0:
                for elem in dictionary[temp_key]:
                    if int(elem[1]) == int(keys):
                        val = elem[-1]
                        if temp_val == val and val == Current_time and temp_val == Current_time:
                            print('Agent {} and Agent {} are in the same group'.format(keys, temp_key))
                            if temp_key not in garray:
                                garray.append(temp_key)
        groups_dict[keys] = garray
                        #print((keys, temp_val),(temp_key, val),end = " ---- ")
        #print("")
    #dict_elem_sort(groups_dict)
    for times in range(16):
        for keys in groups_dict:
            #print(keys," ---> ", groups_dict[keys])
            for elem in groups_dict[keys]:
                for entry in groups_dict[elem]:
                    if entry not in groups_dict[keys]:
                        groups_dict[keys].append(entry)

    groups_accounted = []
    for keys in groups_dict:
        groups_dict[keys].sort()
        if len(groups_dict[keys]) == 0:
            groups_dict[keys].append(keys)
        print(keys, " --->> ",groups_dict[keys])
    for keys in groups_dict:
        if (groups_dict[keys] not in groups_accounted) and (len(groups_dict[keys]) > 0):
            groups_accounted.append(groups_dict[keys])
    
    locations_accounted = []
    for entry in groups_accounted:
        array = []
        for elem in entry:
            array.append(locations[elem])
        locations_accounted.append(array)
    
    for index in range(len(locations_accounted)):
        new = ""
        for entry in locations_accounted[index]:
            new += (str(entry) + "-")
        locations_accounted[index]  = new[:len(new)-1]
    print(locations_accounted)

    for index in range(len(groups_accounted)):
        new = ""
        for entry in groups_accounted[index]:
            new += (str(entry) + "-")
        groups_accounted[index]  = new[:len(new)-1]
    print(groups_accounted)
    time.sleep(3)
    
    
    time.sleep(1)
    '''Abubakr modification'''
    covs_accounted = []

    for index in range(len(locations_accounted)):
        st = ""
        mapp = covmaps[int(groups_accounted[index][0])]
        for i in range(len(mapp)):
            num = str(mapp[i])
            if '-4e' in num:
                index = num.index('-')
                num = num[:index-1]
            test = float(num)
            if test < 0.04:
                num = str(0.0)
            if len(num) > 4:
                num = num[:4]
            st += str(num) + "-"
        st = st[:-1]
        covs_accounted.append(st)

    return numberOfTasks,locations_accounted, groups_accounted, second, threshold, args2, args0, covs_accounted

def call_UDP(numberOfTasks, locations_accounted, groups_accounted, second, threshold, args2, args0, covs_accounted):
    for index in range(len(locations_accounted)):
        cmd = "python3 UDP_script.py " + args0 + " c_a.py "
        cmd += (groups_accounted[index] + " ")
        cmd += (locations_accounted[index] + " ")
        cmd += str(second)
        cmd += f" {threshold}"
        cmd += f" {args2} "
        cmd += covs_accounted[index]

        print(cmd)
        os.system(cmd)
        n = 2
        print(f"---->> Sleeping for {n} seconds <<----")
        time.sleep(2)

    print("======== >>>>> CURRENT STATUS OF THE GRID <<<<<<  ========\n\n")
    print(Task_status(numberOfTasks))
    print("======== >>>>> NOW ENDING THE SCRIPT (pkill method) <<<<<<  ========\n\nScript Status ::::: ", end = " ")
    os.system("pkill -9 -f dynamic.py")
    