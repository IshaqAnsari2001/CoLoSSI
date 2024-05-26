import sys
import os
from optparse import OptionParser
import model_data as Data
import math
from subprocess import Popen, PIPE
import ast
import time
import random
import numpy as np

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
        self.initial_loc = 0
        self.valid_cells = []
        self.valid_tuple = []
        self.valid_tuple_filtered = []
        self.valid = []
        self.meetup_effic = []
        self.meetup_loc = 0
        self.distance = []
        self.workload = []
        self.effic = []
        self.all_dist = []
    
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
        cmd = "python3 c_a.py " + args[0] + " " + groups[i] + " " + locs[i] + " " + str(interval - ti) + " " + args[1] + " " + covs[i] + " " + meetingpos[i]
        #print(cmd)
        #pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
        output = [x.replace("\n","") for x in os.popen(cmd).readlines()]
        curr_ag = [int(x)-1 for x in output[::3]]
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
        cmd = "python3 c_a.py " + args[0] + " " + groups[i] + " " + locs[i] + " " + str(interval - ti) + " " + args[1] + " " + covs[i] + " " + meetingpos[i] + " star " + args[3]
        #print(cmd)
        #pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
        output = [x.replace("\n","") for x in os.popen(cmd).readlines()]
        curr_ag = [int(x)-1 for x in output[::3]]
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

if "t4" in args[0]:
    num_agent = int(args[0][args[0].index("n") + 1 : args[0].index("t4")])
else:
    num_agent = int(args[0][args[0].index("n") + 1 : args[0].index("t2")])

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

allmet = False

#######################################################################################################
#######################################################################################################
'''                                         MY ADDITION                                             '''
#######################################################################################################
#######################################################################################################
import  Meetup_CoLoSSI as CoLoSSI

'''TUNING PARAMETERS'''
meetup_range = [int(instance_type//2),int(round(0.75*instance_type))]
effic_parameter = [4,8,16]
square_diag = int(round(int((meetup_range[0]+meetup_range[1])/2) / 2))

print("MEETUP range :: ",meetup_range,square_diag)

# This loop sets the initial locations for each of the agent.
for i in range(len(groups)):
    t = [int(x) for x in groups[i].split("-")]
    l = [int(x) for x in locs[i].split("-")]
    for j in range(len(t)):
        AGENTS[t[j]-1].initial_loc = l[j]

All_cells = Data.CELLS
grid = []
temp = []
for i in range (len(All_cells)):
    
    if (i != 0 and i % instance_type == 0) or (str(i) == All_cells[-1]): 
        if ((str(i) == All_cells[-1])):
            temp.append(i)
        grid.append(temp)
        temp = []
    temp.append(i)

def get_distance(groups):
    print("GROUPS ::::: ",groups)
    A = [int(x) for x in groups.split("-")]
    # this loop finds all the valid cells that are at a suitable distance
    tup_list = []
    for ag in AGENTS:
        if int(ag.ID) in A:
            ag.distance = []
            ag.effic = []
            ag.workload = []
            print("Agent ID :: ",ag.ID,"  Ini_loc :: ",ag.initial_loc)
            l = [] # holds all valid cells for an agent
            e = []
            for cell_no in All_cells:
                path = CoLoSSI.bfs(CoLoSSI.get_alias(str(ag.initial_loc),str(ag.ID)),CoLoSSI.get_alias(str(cell_no),str(ag.ID)))
                length = len(path) - 1
                if length < meetup_range[0]:
                    ag.distance.append(float(length)/float(meetup_range[0]))
                    alias = str(CoLoSSI.get_alias(str(cell_no),ag.ID))
                    ef  = round(1/Data.expl[(ag.ID,alias,str(cell_no))])
                    ag.effic.append(ef)
                    e.append((cell_no,length))
                if length > meetup_range[1]:
                    ag.distance.append(float(meetup_range[1])/float(length) )
                    alias = str(CoLoSSI.get_alias(str(cell_no),ag.ID))
                    ef  = round(1/Data.expl[(ag.ID,alias,str(cell_no))])
                    ag.effic.append(ef)
                    e.append((cell_no,length))
                if length <= meetup_range[1] and length >= meetup_range[0]:
                    l.append(cell_no)
                    ag.distance.append(1.0)
                    alias = str(CoLoSSI.get_alias(str(cell_no),ag.ID))
                    ef  = round(1/Data.expl[(ag.ID,alias,str(cell_no))])
                    ag.effic.append(ef)
                    e.append((cell_no,length))
            ag.valid_cells = l 
            ag.valid_tuple = e
            ag.all_dist = e
            #print(ag.valid_tuple,len(ag.valid_tuple),"\n")



def generate_enclosure(input):
    center_loc = int(input)
    max_row = instance_type-1
    max_col = max_row
    min_row = 0
    min_col = 0
    
    for r in range(instance_type):
        for c in range(instance_type):
            if center_loc == grid[r][c]:
                row_p = r
                col_p = c
    row_tl = row_p # row_top_left
    col_tl = col_p # column_top_left
    d = square_diag
    while d != 0:
        if (row_tl - 1) == min_row or (col_tl - 1) == min_col:
            if (row_tl - 1) == min_row and (col_tl - 1) != min_col:
                row_tl = min_row
                col_tl -= 1
            if (row_tl - 1) != min_row and (col_tl - 1) == min_col:
                row_tl -= 1
                col_tl = min_col
            if (row_tl - 1) == min_row and (col_tl - 1) == min_col:
                row_tl = min_row
                col_tl = min_col
            break
        else:
            row_tl -= 1
            col_tl -= 1  
            d -= 1 
    
    row_br = row_p  # row_bottom_right
    col_br = col_p  # column_bottom_right
    d = square_diag
    while d != 0:
        if (row_br + 1) == max_row or (col_br + 1) == max_col:
            if (row_br + 1) == max_row and (col_br + 1) != max_col:
                row_br = max_row
                col_br += 1
            if (row_br + 1) != max_row and (col_br + 1) == max_col:
                row_br += 1
                col_br = max_col
            if (row_br + 1) == max_row and (col_br + 1) == max_col:
                row_br = max_row
                col_br = max_col
            break
        else:
            row_br += 1
            col_br += 1  
            d -= 1 

    if row_br >= max_row:
        row_br = max_row

    if row_tl >= max_row:
        row_tl = max_row
    
    if col_br >= max_col:
        col_br = max_col
    
    if col_tl >= max_col:
        col_tl = max_col

    #print("CENTER ::: ",input[0],", row :: ",row_p,", col :: ",col_p)
    #print("TOP LEFT ::: ", grid[row_tl][col_tl],", row :: ",row_tl,", col :: ",col_tl)
    #print(", row :: ",row_br,", col :: ",col_br)
    #print("BOTTOM RIGHT ::: ", grid[row_br][col_br],", row :: ",row_br,", col :: ",col_br)
    temp = []
    for r in range(instance_type):
        for c in range(instance_type):
            if ((r >= row_tl) and (r <= row_br)) and ((c >= col_tl) and (c <= col_br)):
                temp.append(grid[r][c])

    #print(temp)
    return(temp)

def efficacy_normalizer_fucntion(cell_no,ag):
    alias = str(CoLoSSI.get_alias(str(cell_no),ag.ID))
    effic  = round(1/Data.expl[(ag.ID,alias,str(cell_no))])
    result = float((effic - 4)/(16 - 4))
    return(float(1.0 - result))


def get_completed(g_Task_Timings):
    completed = []
    for i in range(len(g_Task_Timings)):
        e = g_Task_Timings[i]
        if e == 0 or (e <= 0.3 and e >= 0):
            completed.append(i)
    return completed

def get_remaining_tasks(enc,completed):
    temp = []
    for e in enc:
        if e not in completed:
            temp.append(e)
    return temp

def workload_mapper(cell_no,g_Task_Timings,ag):
    task_left = g_Task_Timings[cell_no]
    alias = str(CoLoSSI.get_alias(str(cell_no),ag.ID))
    effic  = round(1/Data.expl[(ag.ID,alias,str(cell_no))])
    work_needed = int(round(float(task_left/effic)))
    
    return(work_needed)

def get_effic_and_workload(groups,g_Task_Timings):
    A = [int(x) for x in groups.split("-")]
    for ag in AGENTS:
        if int(ag.ID) in A:
            v = []
            w = []
            for cell_no in Data.CELLS:
                enc = generate_enclosure(cell_no)
                prev_len = len(enc)
                p_enc =enc
                completed = get_completed(g_Task_Timings)
                s = 0
                effic = []
                for c in enc:
                    s += (workload_mapper(c,g_Task_Timings,ag))
                    effic.append(efficacy_normalizer_fucntion(c,ag))
                enc  = get_remaining_tasks(enc,completed)
                number_of_cells = len(enc)
                '''
                if (len(enc)) != prev_len and len(enc) == 0 and prev_len != 0:
                    print("prev ::: ",prev_len)
                    print(p_enc)
                    print(completed)
                    print("New :: ",len(enc))
                    print(enc)
                '''
                if len(enc) != 0:    
                    value1 = float(float(sum(effic))/float(number_of_cells))
                    value2 = float(float(s)/float(number_of_cells))
                    v.append(value1)
                    w.append(value2)
                else:
                    v.append(0.0)
                    w.append(0.0)
            ag.effic = v
            ag.workload = w

def simplify(groups):
    A = [int(x) for x in groups.split("-")]
    array = []
    not_reachable = []
    for ag in AGENTS:
        temp = []
        if int(ag.ID) in A:
            #print("\n\nSIMPLIFIED RESULT FOR agent ID",ag.ID)
            temp.append(ag.distance)
            temp.append(ag.effic)
            temp.append(ag.workload)
            npy = np.array(temp)
            score =  list(np.sum(npy,axis = 0))
            print(len(score))
            array.append(score)
            #print(score, len(score))

            for e in ag.all_dist:
                distance = e[1]
                if distance > interval:
                    not_reachable.append(str(e[0]))
    npy_cum = np.array(array)
    cumulative_score = list(np.sum(npy_cum,axis = 0))
    final = []
    for i in range(len(cumulative_score)):
        if str(i) not in not_reachable:
            final.append(cumulative_score[i])
        else:
            final.append(-1.0)
    if len(final) != (instance_type*instance_type):
        print(final)
        print(len(final),len(cumulative_score))
        print("ERROR")
        exit(0)
    #print("FOR GROUP ",groups, "cumulative score is \n",final)
    m = max(final)
    idx = final.index(m)
    for ag in AGENTS:
        if int(ag.ID) in A:
            ag.meetup_loc = idx

def BLACK_BOX(g,g_Task_Timings):
    get_distance(g)
    get_effic_and_workload(g,g_Task_Timings)
    simplify(g)
    A = [int(x) for x in g.split("-")]
    for ag in AGENTS:
        if int(ag.ID) in A:
             return ag.meetup_loc


#generate_enclosure(('64','4'))
#######################################################################################################
#######################################################################################################
#######################################################################################################

STATS = []
terminate = 2
while not Done:

#    meeting = [random.randint(0,len(Data.CELLS)-1) for x in groups]    # Randomized meeting point
    #meeting = [int(len(Data.CELLS)/2) for x in groups]   # Middle Cell 
    for i in range(len(groups)):
        print(groups[i])
        meeting = BLACK_BOX(groups[i],g_Task_Timings)
        STATS.append(meeting)
        print(" Meeting point for group ",groups[i]," was found to be ",meeting)
        cmd = "python3  Meetup_CoLoSSI.py " + args[0] + " " + groups[i] + " " + locs[i] + " " + str(interval) + " " + args[1] + " " + covs[i] + " " + str(meeting)
        #print(cmd)
        #pipe = Popen(cmd, shell=True, stdout=PIPE).stdout
        output = [x.replace("\n","") for x in os.popen(cmd).readlines()]
        curr_ag = [int(x)-1 for x in output[::3]]
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
    count = 0
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
        

        REGEN = {}
        for ag1 in AGENTS:
            REGEN[ag1.ID] = [ag1]
            for ag2 in AGENTS:
                
                if ag1.ID != ag2.ID and dist(int(ag1.sch[t]) % size,int(ag2.sch[t]) % size) <= int(args[3]):
                    ag1.visited[ag2.ID] = [16 - x for x in ag2.covr]
                    ag2.visited[ag1.ID] = [16 - x for x in ag1.covr]

                    for key in ag2.visited:
                        if key != ag1.ID and (key not in ag1.visited or sum(ag2.visited[key]) > sum(ag1.visited[key])):
                            ag1.visited[key] = ag2.visited[key]

                    if ag2 not in ag1.crewmates and not ag2.recruited:
                        add = True
                        
                        for k in REGEN:
                            if ag2 in REGEN[k]:
                                add = False
                        if add:
                            REGEN[ag1.ID].append(ag2)
                    
        for gr in REGEN:
            if len(REGEN[gr]) != 1:
                star = False

                for ags in REGEN[gr]:
                    if len(ags.crewmates) > 3:
                        star = True
            
                if not star:
                    recruit(REGEN[gr],t,interval)
                
                else:
                    starAlgo(REGEN[gr],t,interval)
          
        if g_Task_Timings == [0] * len(Data.CELLS):
            Done = True
            TotalTime += t + 1
            time2 = time.time()
            print(f"DONE IN {TotalTime} UNITS\n Time taken : {time2-time1/1000}\n")
            print("All meeting points that agents travelled are :: \n",STATS)
            for ag in AGENTS:
                print("schedules :: ",ag.sch)
            sys.exit()
        
    # update loc here
    
    print("\n\ntime ::::: ",TotalTime)
    for ag in AGENTS:
        print("AGent :: ",ag.ID," prev_loc :: ",ag.initial_loc)
        ag.initial_loc = int(ag.sch[-1]) % len(Data.CELLS)
        print("new_loc :: ", ag.initial_loc)

    if not Done:
        TotalTime += interval
        interval = newinterval()
    
    groups, locs, covs = find_new()
    



