import socket
import os
import sys
import math
from optparse import OptionParser
import model_data as Data

def get_cmd(file_name, INSTAN, group, locations, threshold, argu, covs):
    spli = INSTAN.split("_")
    unit = ""
    
    for elem in spli:
        if 'n' in elem and 't' in elem:
            unit = elem
    unit = unit[1:].split("t")[:1]
    agent_no = unit[0]
    cmd = "python3 "+ file_name + " " + INSTAN + " " + group + " " + locations + " " + threshold 
    cmd = cmd + f" {argu} " + covs
    All_agent = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16']
    All_agent = All_agent[:int(agent_no)]
    return cmd, All_agent

class agent_info():
    def __init__(self,agent):
        self.ID = agent
        self.schedule = []
        self.raw_sch = []
        self.timings = []

if __name__ == "__main__":
    usage = "usage: %prog [options] mdata"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()
    #print(args, len(args))
    if len(args) not in [8]:
        print("Invalid number of arguments")
        sys.exit(0)
    Data.readMDATA(args[0])
    # args[0] == INSTANCE NAME
    # args[1] == FILE NAME
    # args[2] == groups
    # args[3] == agent locations
    # args[4] == current time
    # args[5] == Threshold
    # args[6] == meetup/nomeetup
    # args[7] == Tasks coverage list

    cmd, All_agent = get_cmd(args[1],args[0], args[2],args[3],args[5],args[6], args[7])

    threshold = int(args[5])
    cmd = str(cmd)
    output = os.popen(cmd).read()
    print(":::::::::::::::::::::::::::::: OUTPUT FROM ALGO ::::::::::::::::::::::::::")
    print(output)
    output = output.split("\n")
    
    AGENT_OBJ = []
    for agent in All_agent:
        AGENT_OBJ.append(agent_info(agent))
    new_all_agents = args[2].split("-")
    #print(new_all_agents)
    NEW_AGENT_OBJ = []
    for ag in AGENT_OBJ:
        if ag.ID in new_all_agents:
            NEW_AGENT_OBJ.append(ag)
    #print(len(NEW_AGENT_OBJ))
    schedules =[]
    times = []
    agent = []
    for i in range(len(output)):
        if i % 3 == 0:
            agent.append(output[i])
        if i % 3 == 1:
            schedules.append(output[i])
        if i % 3 == 2:
            times.append(output[i])
    
    for entry in agent:
        if len(entry) == 0:
            index = agent.index(entry)
            del agent[index]

    for i in range(len(agent)):
        for ag in NEW_AGENT_OBJ:
            if agent[i] == str(ag.ID):
                ag.schedule  =  str(schedules[i])
                ag.timings = str(times[i])

    for ag in NEW_AGENT_OBJ:
        if len(ag.schedule) > 0 and len(ag.timings) > 0:
            ag.schedule = ag.schedule.split(",")
            ag.schedule[0] =  ag.schedule[0][1:]
            ag.schedule[-1] = ag.schedule[-1][:len(ag.schedule[-1]) - 1]
            ag.timings = (ag.timings).split(",")
            ag.timings[0] =  ag.timings[0][1:]
            ag.timings[-1] = ag.timings[-1][:len(ag.timings[-1]) - 1]
    
    



    print(":::::::::::::::::::::::::::: OUTPUT GIVEN TO SIM :::::::::::::::::::::::::::::")
    for ag in NEW_AGENT_OBJ:
        print(ag.ID)
        print(ag.schedule, len(ag.schedule))
        print(ag.timings, len(ag.timings))
        print('\n')


    with open("commands.txt", "w") as cmds:
        default = "TASK "
        for ag in NEW_AGENT_OBJ:
            start_time = int(args[4])
            for index in range(len(ag.schedule)):
                #print(ag.timings[index])
                string = str(default + str(ag.ID)+" "+ str(index + 1)+" "+ str(start_time) +" "+ str(int(start_time) + int(int(ag.timings[index]) * 300))) +" "+str(ag.schedule[index].strip()) +"\n"
                start_time = int(start_time) + int(int(ag.timings[index]) * 300)
                cmds.writelines(string)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('localhost', 5000)
    #sock.bind(server_address)

    with open("commands.txt", "r") as cmds:
        data = cmds.readline()
        while data:
            sent = sock.sendto(bytes(data, 'UTF-8'), ('localhost', 12345))
            data = cmds.readline()  