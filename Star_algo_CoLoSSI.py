import sys
import os
from optparse import OptionParser
import model_data as Data
import math
from subprocess import Popen, PIPE
import ast
import time
import random

### Update - inter-agent coverage map
class robot():
    def __init__(self,id):
        self.ID = id
        self.sch = []
        self.times = []
        self.covr = []
        self.visited = {}
        self.meeting = 0
        self.crewmates = []
        self.recruited = False

    
    def __eq__(self, other):
        return isinstance(other,robot) and self.ID == other.ID

    def __hash__(self):
        return int(self.ID)

def dist(start,finish):
    n = int(math.sqrt(len(Data.CELLS)))
    row1, col1 = int(start) // n, int(start) % n
    row2, col2 = abs((int(finish) // n) - row1), abs((int(finish) % n) - col1)

    return max(row2,col2)

def find_new():

    #ALL = False
    check = AGENTS.copy()
    size = len(Data.CELLS)
    groups = []
    locs = []
    covf = []
    accounted = [False] * (len(AGENTS)+1)
    for ag in AGENTS:
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
    


def runAlgo(groups,meetingpos,locs,interval,covs,ti):

    for i in range(len(groups)):
        cmd = "python3 Meetup_CoLoSSI.py " + args[0] + " " + groups[i] + " " + locs[i] + " " + str(interval - ti) + " " + args[1] + " " + covs[i] + " " + meetingpos[i]
        #print(cmd)
        #pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
        output = [x.replace("\n","") for x in os.popen(cmd).readlines()]
        curr_ag = [int(x) for x in output[::3]]
        k = i
        i = 1
        for ag in curr_ag:
            
            #print(ag+1)
            #AGENTS[ag].sch = ast.literal_eval(output[i])
            #AGENTS[ag].times = ast.literal_eval(output[i+1])
            new_sch = ast.literal_eval(output[i])
            new_tim = ast.literal_eval(output[i+1])

            sch = []

            for k in range(len(new_tim)):
                sch += [new_sch[k]] * int(new_tim[k])
            
            if sch != []:
                AGENTS[ag].sch = AGENTS[ag].sch[:ti+1] + sch[:interval - ti - 1]
            else:
                AGENTS[ag].sch = [AGENTS[ag].sch[-1]] * (interval)
            
            if len(AGENTS[ag].sch) < interval:
                AGENTS[ag].sch += [AGENTS[ag].sch[-1]] * (interval - len(AGENTS[ag].sch))

            

            assert(len(AGENTS[ag].sch) == interval)
            AGENTS[ag].group = k
            AGENTS[ag].meeting = AGENTS[ag].sch[-1]
            

            i+=3
            #print(AGENTS[ag].ID)
            #print(AGENTS[ag].sch)

def newinterval():

    #num = len([x for x in g_Task_Timings if x == 0])
    #partition = len(Data.CELLS) // 4


    return int(args[2])

def runStarAlgo(groups,meetingpos,locs,interval,covs,ti):

    for i in range(len(groups)):
        cmd = "python3 Meetup_CoLoSSI.py " + args[0] + " " + groups[i] + " " + locs[i] + " " + str(interval - ti) + " " + args[1] + " " + covs[i] + " " + meetingpos[i] + " star " + args[3]
        #print(cmd)
        #pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
        output = [x.replace("\n","") for x in os.popen(cmd).readlines()]
        curr_ag = [int(x) for x in output[::3]]
        k = i
        i = 1
        for ag in curr_ag:
            
            #print(ag+1)
            #AGENTS[ag].sch = ast.literal_eval(output[i])
            #AGENTS[ag].times = ast.literal_eval(output[i+1])
            new_sch = ast.literal_eval(output[i])
            new_tim = ast.literal_eval(output[i+1])

            sch = []

            for k in range(len(new_tim)):
                sch += [new_sch[k]] * int(new_tim[k])
            
            if sch != []:
                AGENTS[ag].sch = AGENTS[ag].sch[:ti+1] + sch[:interval - ti - 1]
            else:
                AGENTS[ag].sch = [AGENTS[ag].sch[-1]] * (interval)
            
            if len(AGENTS[ag].sch) < interval:
                AGENTS[ag].sch += [AGENTS[ag].sch[-1]] * (interval - len(AGENTS[ag].sch))

            

            assert(len(AGENTS[ag].sch) == interval)
            AGENTS[ag].group = k
            AGENTS[ag].meeting = AGENTS[ag].sch[-1]
            

            i+=3
            #print(AGENTS[ag].ID)
            #print(AGENTS[ag].sch)

def recruit (gr,ti,interval):

    maxag = 0  

    crewtasks = []

    for ag in gr:
        crewtasks.append(sum([sum(x.covr) for x in ag.crewmates]))

    for i in range(len(gr)):

        if crewtasks[i] > crewtasks[maxag]:
            maxag = i

        elif crewtasks[i] == crewtasks[maxag]:
            if len(gr[i].crewmates) > len(gr[maxag].crewmates):
                maxag = i
    
    locs = []

    for agg in gr:
        locs.append(int(agg.sch[ti]) % len(Data.CELLS))

    lcc = ""

    for lo in locs:
        lcc += str(lo) + "-"
    lcc = lcc[:-1]

    grpcov = {}

    for ag in gr:
        for team in ag.visited:
            if team not in grpcov:
                grpcov[team] = ag.visited[team]
            else:
                if sum(ag.visited[team]) > sum(grpcov[team]):
                    grpcov[team] = ag.visited[team]
    
    for ag in gr:
        for ag2 in grpcov:
            if ag.ID != ag2:
                ag.visited[ag2] = grpcov[ag2]
    
    firstag = gr[0]

    worklist = [16 - x for x in firstag.covr]

    for secag in firstag.visited:
        for j in range(size):
            worklist[j] += firstag.visited[secag][j]
    
    grptasks = [max(16 - x,0) for x in worklist]

    covst = ""
    for k in range(size):
        covst += str(grptasks[k] / 16) + "-"
    covst = covst[:-1]

    for ag in gr:
        if ag != gr[maxag]:
            crews = gr[maxag].crewmates + gr
            while ag in crews:
                crews.remove(ag)
            ag.crewmates = list(set(crews))
    
    grps = [str(x.ID) for x in gr]

    grep = ""
    for a in grps:
        grep += a + "-"
    grep = grep[:-1]

    for ag1 in gr:
        ag1.recruited = True

    runAlgo([grep],[str(gr[maxag].meeting)],[lcc],interval,[covst],ti)


def starAlgo (gr,ti,interval):

    maxag = 0  

    crewtasks = []

    for ag in gr:
        crewtasks.append(sum([sum(x.covr) for x in ag.crewmates]))

    for i in range(len(gr)):

        if crewtasks[i] > crewtasks[maxag]:
            maxag = i

        elif crewtasks[i] == crewtasks[maxag]:
            if len(gr[i].crewmates) > len(gr[maxag].crewmates):
                maxag = i
    
    locs = []

    for agg in gr:
        locs.append(int(agg.sch[ti]) % len(Data.CELLS))

    lcc = ""

    for lo in locs:
        lcc += str(lo) + "-"
    lcc = lcc[:-1]

    grpcov = {}

    for ag in gr:
        for team in ag.visited:
            if team not in grpcov:
                grpcov[team] = ag.visited[team]
            else:
                if sum(ag.visited[team]) > sum(grpcov[team]):
                    grpcov[team] = ag.visited[team]
    
    for ag in gr:
        for ag2 in grpcov:
            if ag.ID != ag2:
                ag.visited[ag2] = grpcov[ag2]
    
    firstag = gr[0]

    worklist = [16 - x for x in firstag.covr]

    for secag in firstag.visited:
        for j in range(size):
            worklist[j] += firstag.visited[secag][j]
    
    grptasks = [max(16 - x,0) for x in worklist]

    covst = ""
    for k in range(size):
        covst += str(grptasks[k] / 16) + "-"
    covst = covst[:-1]

    for ag in gr:
        if ag != gr[maxag]:
            crews = gr[maxag].crewmates + gr
            while ag in crews:
                crews.remove(ag)
            ag.crewmates = list(set(crews))
    
    grps = [str(x.ID) for x in gr]

    grep = ""
    for a in grps:
        grep += a + "-"
    grep = grep[:-1]

    for ag1 in gr:
        ag1.recruited = True

    runStarAlgo([grep],[str(gr[maxag].meeting)],[lcc],interval,[covst],ti)

### MDATA FILE 
#### MEETUP / NOMEETUP 
### CELL RESTRICTION
usage = "usage: %prog [options] mdata"
parser = OptionParser(usage=usage)

(options, args) = parser.parse_args()

Data.readMDATA(args[0])
time1 = time.time()
meetup = False
if args[1] == "meetup":
    meetup = True
elif args[1] != "nomeetup":
    print("second arg error")
    sys.exit()

interval = int(args[2])

g_Task_Timings = [16] * len(Data.CELLS)

new = False

if "t4" in args[0]:
    num_agent = int(args[0][args[0].index("n") + 1 : args[0].index("t4")])
elif "t2" in args[0]:
    num_agent = int(args[0][args[0].index("n") + 1 : args[0].index("t2")])
else:
    num_agent = int(args[0][args[0].index("n") + 1 : args[0].index("t3")])
    new = True

if not new:
    instance_type = int(args[0][args[0].index("L") + 1 : args[0].index("-")])
else:
    instance_type = 10
    
#print(instance_type)


## Hardcoded
if num_agent == 4:
    if instance_type == 10:
        groups = ["0-1","2-3"]
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

AGENTS = [robot(str(x)) for x in range(0,num_agent)]
for ag in AGENTS:
    ag.covr = [16] * len(Data.CELLS)

Done = False
TotalTime = 0

allmet = False

firsttime = True


alll = []
while not Done:

    #meeting = [random.randint(0,len(Data.CELLS)-1) for x in groups]    # Randomized meeting point
    meeting = [int(len(Data.CELLS)/2) for x in groups]   # Middle Cell 
 
    for i in range(len(groups)):
        if firsttime:
            cmd = "python3 Meetup_CoLoSSI.py " + args[0] + " " + groups[i] + " " + locs[i] + " " + str(interval) + " " + args[1] + " " + covs[i] + " " + str(meeting[i])
            firsttime = False
            #firstime = False
        else:
            cmd = "python3 Meetup_CoLoSSI.py " + args[0] + " " + groups[i] + " " + locs[i] + " " + str(interval) + " " + args[1] + " " + covs[i]
        #print(cmd)
        #pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
        output = [x.replace("\n","") for x in os.popen(cmd).readlines()]
        curr_ag = [int(x) for x in output[::3]]
        k = i
        i = 1
        for ag in curr_ag:
            
            #print(ag+1)
            #AGENTS[ag].sch = ast.literal_eval(output[i])
            #AGENTS[ag].times = ast.literal_eval(output[i+1])
            new_sch = ast.literal_eval(output[i])
            new_tim = ast.literal_eval(output[i+1])

            sch = []

            for k in range(len(new_tim)):
                sch += [new_sch[k]] * int(new_tim[k])
            
            if sch != []:
                AGENTS[ag].sch = sch[:interval]
            else:
                AGENTS[ag].sch = [AGENTS[ag].sch[-1]] * interval
            
            if len(AGENTS[ag].sch) < interval:
                AGENTS[ag].sch += [AGENTS[ag].sch[-1]] * (interval - len(AGENTS[ag].sch))
                
            AGENTS[ag].crewmates = []
            assert(len(AGENTS[ag].sch) == interval)
            AGENTS[ag].group = k
            AGENTS[ag].meeting = AGENTS[ag].sch[-1]
            AGENTS[ag].recruited = False
            #print(AGENTS[ag].sch[-1])

            for ag2 in curr_ag:
                if ag != ag2:
                    AGENTS[ag].crewmates.append(AGENTS[ag2]) 

            i+=3
            #print(AGENTS[ag].ID)
            #print(AGENTS[ag].sch)
    #print("ROUND DONE \n \n")
    size = len(Data.CELLS)
    
    for t in range(interval):

        #At this time all agents formed one group
        if len(groups) == 1 and not allmet:
            print(f"ALL AGENTS MET AT {TotalTime + t + 1}")  
            allmet = True   

        for ag in AGENTS:
            if t < len(ag.sch):
                g_Task_Timings[int(ag.sch[t]) % size] -= round(Data.expl[(ag.ID,str(ag.sch[t]),str(int(ag.sch[t]) % size))] * 16)
                ag.covr[int(ag.sch[t]) % size] -= round(Data.expl[(ag.ID,str(ag.sch[t]),str(int(ag.sch[t]) % size))] * 16)

                if g_Task_Timings[int(ag.sch[t]) % size] < 0:
                    g_Task_Timings[int(ag.sch[t]) % size] = 0
                
                if ag.covr[int(ag.sch[t]) % size] < 0:
                    ag.covr[int(ag.sch[t]) % size] = 0
        
        alll.append([ag.sch[t] for ag in AGENTS])
        if t % 5 == 0:
            REGEN = {}
            for ag1 in AGENTS:

                new = True
                index = ag1.ID

                for k in REGEN:
                    if ag1 in REGEN[k]:
                        new = False
                        index = k
                
                if new:
                    REGEN[ag1.ID] = [ag1]
                
                for ag2 in AGENTS:
                    
                    if ag1.ID != ag2.ID and dist(int(ag1.sch[t]) % size,int(ag2.sch[t]) % size) <= int(args[3]):
                        ag1.visited[ag2.ID] = [16 - x for x in ag2.covr]
                        ag2.visited[ag1.ID] = [16 - x for x in ag1.covr]

                        for key in ag2.visited:
                            if key != ag1.ID and (key not in ag1.visited or sum(ag2.visited[key]) > sum(ag1.visited[key])):
                                ag1.visited[key] = ag2.visited[key]

                        if not ag2.recruited:
                            add = True
                            
                            for k in REGEN:
                                if ag2 in REGEN[k]:
                                    add = False
                            if add:
                                REGEN[index].append(ag2)
            
            if t == 0:
                print(groups)
                print([[x.ID for x in REGEN[k]] for k in REGEN])    
            
            for gr in REGEN:

                if len(REGEN[gr]) != 1:
                    star = False

                    if len(REGEN[gr]) > 3 and args[4].lower() == "star":
                        star = True
                
                    if not star:
                        recruit(REGEN[gr],t,interval)
                    
                    else:
                        print("star algo")
                        starAlgo(REGEN[gr],t,interval)

        if g_Task_Timings == [0] * len(Data.CELLS):
            Done = True
            TotalTime += t + 1
            time2 = time.time()
            print(f"DONE IN {TotalTime} UNITS\n Time taken : {time2-time1/1000}\n")
            #print(alll)
            sys.exit()
    

    if not Done:
        TotalTime += interval
        interval = newinterval()
    
    groups, locs, covs = find_new()
    



