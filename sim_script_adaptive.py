import sys
import os
from optparse import OptionParser
import model_data as Data
import math
from subprocess import Popen, PIPE
import ast

### Update - inter-agent coverage map
class robot():
    def __init__(self,aid):
        self.ID = aid
        self.sch = []
        self.times = []
        self.covr = []
        self.count = 0
        #self.interval = 5
        self.visited = {}

def dist(start,finish):
    n = int(math.sqrt(len(Data.CELLS)))
    row1, col1 = int(start) // n, int(start) % n
    row2, col2 = abs((int(finish) // n) - row1), abs((int(finish) % n) - col1)

    return max(row2,col2)

def find_interval(covs):
    tasklist = [float(x) == 0 for x in covs.split("-")]

    #print(tasklist)

    complete = tasklist.count(True)

    if complete <= 25:
        return 5

    elif complete <= 50:
        return 7
    
    elif complete <= 75:
        return 9
    
    else:
        return 11

def get_sch(groups,locs,interval,covs):
        #for i in range(len(groups)):
        cmd = "python3 c_a.py " + args[0] + " " + groups + " " + locs + " " + str(interval) + " " + args[1] + " " + covs
        #print(cmd)
        #pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
        output = [x.replace("\n","") for x in os.popen(cmd).readlines()]
        curr_ag = [int(x)-1 for x in output[::3]]
        i = 1
        for ag in curr_ag:
            
            #print(ag+1)
            old_len = len(AGENTS[ag].sch)
            #AGENTS[ag].sch = ast.literal_eval(output[i])
            #AGENTS[ag].times = ast.literal_eval(output[i+1])
            new_sch = ast.literal_eval(output[i])
            new_tim = ast.literal_eval(output[i+1])

            sch = []

            for k in range(len(new_tim)):
                sch += [new_sch[k]] * int(new_tim[k])
            
            '''if AGENTS[ag].ID == "1":
                print(f"BEFORE {AGENTS[ag].sch}")
                '''
            if sch != []:
                AGENTS[ag].sch += sch[:interval]
            else:
                AGENTS[ag].sch += [AGENTS[ag].sch[-1]] * interval
            
            if len(sch) < interval and len(sch) > 0:
                AGENTS[ag].sch += [AGENTS[ag].sch[-1]] * (interval - len(sch))
                
            '''if AGENTS[ag].ID == "1":
                print(f"AFTER {AGENTS[ag].sch}")'''
            assert(len(AGENTS[ag].sch) - old_len == interval)
            i+=3
            #print(AGENTS[ag].ID)
            #print(AGENTS[ag].sch)
        #print("ROUND DONE \n \n")

def find_new(REGEN):

    #ALL = False
    check = REGEN.copy()
    size = len(Data.CELLS)
    groups = []
    locs = []
    covf = []
    accounted = [False] * (len(AGENTS)+1)
    for ag in REGEN:
        if not accounted[int(ag.ID)]:
            if ag in check:
                check.remove(ag)
            #print(len(check))
            group = [ag]
            add = True
            while add:
                add = False
                #for ag2 in check:
                for ag3 in group:
                    for ag2 in check:
                        if dist(int(ag2.sch[-1]) % size, int(ag3.sch[-1]) % size) <= int(args[3]) and ag2 not in group:
                            group += [ag2]
                            #print(check)
                            #print(ag2)
                            check.remove(ag2)
                            add = True

            newgrp = [x.ID for x in group]
            for n in newgrp:
                accounted[int(n)] = True
            
            groups.append([x.ID for x in group])
            covf.append(group)
            locs.append([int(x.sch[-1])% size for x in group])

    finalg, finallc = [], []
    for i in range(len(groups)):
        grp = ""
        lcc = ""
        for k in range(len(groups[i])):
            grp += groups[i][k] + "-"
            lcc += str(locs[i][k]) + "-"
        grp = grp[:-1]
        lcc = lcc[:-1]
        finalg.append(grp)
        finallc.append(lcc)
    
    finalcovs = []

    for group in covf:

        grpcov = {}

        for ag in group:
            for team in ag.visited:
                if team not in grpcov:
                    grpcov[team] = ag.visited[team]
                else:
                    if sum(ag.visited[team]) > sum(grpcov[team]):
                        grpcov[team] = ag.visited[team]
        
        for ag in group:
            for ag2 in grpcov:
                if ag.ID != ag2:
                    ag.visited[ag2] = grpcov[ag2]
        
        firstag = group[0]

        worklist = [16 - x for x in firstag.covr]

        for secag in firstag.visited:
            for j in range(size):
                worklist[j] += firstag.visited[secag][j]
        
        grptasks = [max(16 - x,0) for x in worklist]

        covst = ""
        for k in range(size):
            covst += str(grptasks[k] / 16) + "-"
        covst = covst[:-1]
        finalcovs.append(covst)
        
    return finalg,finallc,finalcovs
    

usage = "usage: %prog [options] mdata"
parser = OptionParser(usage=usage)

(options, args) = parser.parse_args()

Data.readMDATA(args[0])

meetup = False
if args[1] == "meetup":
    meetup = True
elif args[1] != "nomeetup":
    print("second arg error")
    sys.exit()


### MDATA FILE 
#### MEETUP / NOMEETUP 
#### Replanning Interval
### CELL RESTRICTION

interval = int(args[2])
#interval = 5    

g_Task_Timings = [16] * len(Data.CELLS)

num_agent = int(args[0][args[0].index("n") + 1 : args[0].index("t4")])
instance_type = int(args[0][args[0].index("L") + 1 : args[0].index("-")])
#print(instance_type)
if num_agent == 4:
    if instance_type == 10:
        groups = ["1-2","3-4"]
        locs = ["0-0","99-99"]
    elif instance_type == 20:
        locs = ['0-0', '399-399']
        groups = ['1-2', '3-4']

elif num_agent == 6:
    if instance_type == 10:
        groups = ["1-6","2-3","4-5"]
        locs = ["0-0","99-99","90-90"]
    elif instance_type == 20:
        locs = ['0-0', '399-399', '380-380']
        groups = ['1-6', '2-3', '4-5']

elif num_agent == 8:
    if instance_type == 10:
        groups = ["1-4","5-8","2-7","3-6"]
        locs = ["0-0","99-99","90-90","9-9"]
    elif instance_type == 20:
        groups = ["1-4","5-8","2-7","3-6"]
        locs = ["0-0","399-399","380-380","19-19"]

elif num_agent == 10:
    if instance_type == 10:
        groups = ["1-8-10","3-4","2-6","5-7-9"]
        locs = ["0-0-0","99-99","90-90","9-9-9"]
    elif instance_type == 20:
        groups = ["1-8-10","3-4","2-6","5-7-9"]
        locs = ["0-0-0","399-399","380-380","19-19-19"]


elif num_agent == 12:
    if instance_type == 10:
        groups = ["1-4-7","3-5-6","8-10-12","2-9-11"]
        locs = ["0-0-0","99-99-99","90-90-90","9-9-9"]
    elif instance_type == 20:
        groups = ["1-4-7","3-5-6","8-10-12","2-9-11"]
        locs = ["0-0-0","399-399-399","380-380-380","19-19-19"]


elif num_agent == 14:
    if instance_type == 10:
        groups = ["1-5-9-12","3-7-11","4-8-14","2-6-10-13"]
        locs = ["0-0-0-0","99-99-99","90-90-90","9-9-9-9"]
    elif instance_type == 20:
        groups = ["1-5-9-12","3-7-11","4-8-14","2-6-10-13"]
        locs = ["0-0-0-0","399-399-399","380-380-380","19-19-19-19"]


elif num_agent == 16:
    if instance_type == 10:
        groups = ["1-5-9-13","3-7-15","2-4-6-8-10-12-16","11-14"]
        locs = ["0-0-0-0","99-99-99","90-90-90-90-90-90-90","9-9"]
    elif instance_type == 20:
        groups = ["1-5-9-13","3-7-15","2-4-6-8-10-12-16","11-14"]
        locs = ["0-0-0-0","399-399-399","380-380-380-380-380-380-380","19-19"]


else:
    print("number agent error")
    sys.exit()

cov = ""
for i in range(len(Data.CELLS)):
    cov += "1.0-"
cov = cov[:-1]

covs = [cov] * len(groups)

AGENTS = [robot(str(x)) for x in range(1,num_agent+1)]
for ag in AGENTS:
    ag.covr = [16] * len(Data.CELLS)

Done = False
TotalTime = 0

t = 0

for m in range(len(groups)):
    get_sch(groups[m],locs[m],interval,covs[m])
while not Done:
    
    size = len(Data.CELLS)
    
    for ag in AGENTS:
        #print(ag.sch)
        if t < len(ag.sch):
            g_Task_Timings[int(ag.sch[t]) % size] -= round(Data.expl[(ag.ID,str(ag.sch[t]),str(int(ag.sch[t]) % size))] * 16)
            ag.covr[int(ag.sch[t]) % size] -= round(Data.expl[(ag.ID,str(ag.sch[t]),str(int(ag.sch[t]) % size))] * 16)

            if g_Task_Timings[int(ag.sch[t]) % size] < 0:
                g_Task_Timings[int(ag.sch[t]) % size] = 0
            
            if ag.covr[int(ag.sch[t]) % size] < 0:
                ag.covr[int(ag.sch[t]) % size] = 0
    
    for ag1 in AGENTS:
        for ag2 in AGENTS:
            
            '''print(t)
            print(ag1.ID,len(ag1.sch))
            print(ag2.ID,len(ag2.sch))
            print("")'''
            if t < len(ag1.sch) and t < len(ag2.sch):
                if ag1.ID != ag2.ID and dist(int(ag1.sch[t]) % size,int(ag2.sch[t]) % size) <= int(args[3]):
                    ag1.visited[ag2.ID] = [16 - x for x in ag2.covr]
                    ag2.visited[ag1.ID] = [16 - x for x in ag1.covr]

                    for key in ag2.visited:
                        if key != ag1.ID and (key not in ag1.visited or sum(ag2.visited[key]) > sum(ag1.visited[key])):
                            ag1.visited[key] = ag2.visited[key]

    if g_Task_Timings == [0] * len(Data.CELLS):
        Done = True
        TotalTime = t + 1

        calibcount = [x.count for x in AGENTS]
        print(f"DONE IN {TotalTime} UNITS")
        print(f"Maximum # of calibrations is {max(calibcount)} and the average is {sum(calibcount)/len(AGENTS)}\n")
        sys.exit()
    
    REGEN = []
    for ag in AGENTS:
        
        if t == (len(ag.sch) - 1):
            REGEN.append(ag)
            ag.count += 1

    if REGEN != []:

        groups, locs, covs = find_new(REGEN)

        for m in range(len(groups)):
            tinterval = find_interval(covs[m])
            get_sch(groups[m],locs[m],tinterval,covs[m])

    t += 1

    #groups, locs, covs = find_new(AGENTS)
    #print(groups)

