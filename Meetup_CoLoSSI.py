import sys
from optparse import OptionParser
import model_data as Data
import math
import random
import time as TI

from simulator_interface import *

AGENT_OBJ = []

def All_Tasks_s():
    print(All_Tasks)


def get_alias(cell_no, agID):
    
    for i in Data.riLoc[cell_no]: # Data.riLoc[cell_no] is the List of all task alias associated with that cell number.
        if i in Data.ALoc[agID]: # Data.ALoc[agID] is the List of all the tasks the particular agent can do.
            return(i)

def check(agent):
    temp = [str(x) for x in agent.schedule]
    temp = convert(temp,agent)

    for i in range(len(temp)-1):
        
        if temp[i+1] not in Data.ADJ[temp[i]]:
            return False

    return True

def convert(path,agent):
    add = len(Data.CELLS)
    path = [int(x)%add for x in path]
    need = 0
    while True:
        if str(path[0]) in agent.locs:
            break
        else:
            path[0] += add
            need += add
    
    for i in range(1,len(path)):
        path[i] = path[i] + need

    return [str(x) for x in path]

def pathfinder2(pathlist):
    
    best = pathlist[0]
    bestsum = 0
    size = len(Data.CELLS)

    for i in pathlist:
        pathsum = 0

        for t in i[1:]:
            if Visited[int(t)%size]:
                pathsum +=1
                #pathsum += min(Tasks_Timings[int(t)%size],round(Data.expl[(agent.ID,agent.locs[int(t)%size],str(int(t)%size))] * 16))

        if pathsum < bestsum:
            bestsum = pathsum
            best = i

    return best

def pathfinder(pathlist,target):
    c = pathlist[int(target)%len(Data.CELLS)]
    path = [target]

    while c != None:
        path.insert(0,c)
        c = pathlist[int(c)%len(Data.CELLS)]
    
    return path

def bfs(start,target):

    visited = [False] * len(Data.CELLS)

    queue = []

    queue.append(start)
    visited[int(start)%len(Data.CELLS)] = True

    prev = [None] * len(Data.CELLS)

    while queue != []:
        current = queue.pop(0)

        tlist = Data.ADJ[str(current)]
        #random.shuffle(tlist)
        for t in tlist:
            if visited[int(t)%len(Data.CELLS)] == False:
                queue.append(t)
                visited[int(t)%len(Data.CELLS)] = True
                prev[int(t)%len(Data.CELLS)] = current

        if visited[int(target)%len(Data.CELLS)]:
            return pathfinder(prev,target)

def BFSR(start,target,n):
    if (start,target) in Bfs_Ans:
        return pathfinder2(Bfs_Ans[(start,target)])

    paths = []
    for i in range(n):
       ans = bfs(start,target)
       if ans not in paths:
           paths.append(ans)
    
    Bfs_Ans[(start,target)] = paths
    return(pathfinder2(paths))

def all_path_returner(start,target,agent,Tasks_Left):
    answers = []
    size = len(Data.CELLS)
    distances = [float('inf')] * size
    minimum_dist = float('inf')
    queue = []
    queue.append(node(start,[start],0))
    distances[int(start)%size] = 0

    while queue != []:
        current = queue.pop(0)
        if current.distance > minimum_dist:
            pass

        if current.task == target:
            minimum_dist = current.distance
            answers.append(current)

        elif current.distance < minimum_dist:
            for t in Data.ADJ[current.task]:
                if distances[int(t)%size] >= current.distance + 1:
                    queue.append(node(t,current.path+[t],current.distance+1))
                    distances[int(t)%size] = current.distance + 1  

    paths = []
    for ans in answers:
        if len(ans.path) >= 3:
            path = ans.path
            for i in range(len(path)):
                task = path[i]
                path[i] = int(task) % len(Data.CELLS)
            paths.append(path)

    path_with_left_task = []
    for way in paths:
        road = way
        del road[0]
        del road[-1]
        for t in road:
            if t in Tasks_Left:
                path_with_left_task.append(way)

    if len(path_with_left_task) != 0:
        return path_with_left_task
    else: 
        return None

class node:
    def __init__(self,task,path,distance):
        self.task = task
        self.path = path
        self.distance = distance

class agent_info():
    def __init__(self,agent):
        self.ID = agent
        self.locs = Data.ALoc[agent]
        self.initial_loc = Data.initLoc[str(self.ID)]
        self.schedule = []
        self.bid = 0
        self.timings = []
        self.won = []

    def Generate_bid(self, task, bidding, work, sch, time, pa,ka): 
        self.bid = 0     
        
        alias = str(get_alias(task,self.ID))
        path =  BFSR(self.initial_loc,alias, 1)
        if len(path) > 1:
            path_length = len(path) - 2
        else:
            # assert(len(path) == 1)
            path_length = 0
        #print(sum(self.timings))
        
        '''
        *************************************************************************
                                        *NOTE*
        *************************************************************************
        HERE WE HAVE ADDED THE FUNCTIONALITY THAT THE AGENTS WILL MOVE TOWARDS 
        THE DESIGNATED MEETUP POINTS/CELL AS DEFINED IN THE ARGUMENT.
        THIS WILL MOSTLY BE CALLED BY THE FILE sim_script.py AND WILL BE USED WITH
        STAR TOPOLOGY.
        *************************************************************************
        '''

        if len(args) > 6:        
            meetingal = str(get_alias(str(int(args[6])% len(Data.CELLS)),self.ID))
            meetingpath = BFSR(self.initial_loc,meetingal, 1)
            ptl = len(meetingpath)
            if len(meetingpath) > 1:
                ptl -= 2
            else:
                ptl = 0
        else:
            ptl = 0
        

        '''HERE THE PT1 IS THE FACTOR THAT WE MULTIPLY WITH IN THE BID'''
        val = work * min(round(1/Data.expl[(self.ID,alias,str(task))]),math.ceil(Tasks_Timings[int(task)] / (16 * Data.expl[(self.ID,alias,str(task))])))
        val += sch * len(self.schedule) + time * sum(self.timings) + pa * path_length + ka * ptl
    
        self.bid = val
        return(val)

    def search_for_tasks(self,task):
        #alias = str(get_alias(str(task),self.ID))
        count = 0
        for tasks in self.schedule: 
            if tasks == task:
                count = self.schedule.count(task)

        #effic = round(1/Data.expl[(self.ID,alias,str(task))])

        return count

    def get_task_efficacy(self,task):
        alias = str(get_alias(str(task),self.ID))
        if task in self.schedule:
            effic = round(1/Data.expl[(self.ID,alias,str(task))])
            return effic
        else:
            return "nope"


    def reset_agent_overkill(self):
        for i in range(len(self.schedule)):
            task = self.schedule[i]
            alias = str(get_alias(str(task),self.ID))
            effic = round(1/Data.expl[(self.ID,alias,str(task))])
            current_unit = self.timings[i]
            count = self.schedule.count(task)
            if current_unit > 1:
                if Tasks_Timings[int(task)] < 0:
                    #print("Agent :: ",self.ID, " does task ", task, "with effic ",effic," and invests ",self.timings[i])
                    #print("overkill found at end was :: ",Tasks_Timings[int(task)])
                    reduces = math.floor (math.floor( abs(Tasks_Timings[int(task)]) / (16 * (1/effic)) ) / count)
                    #print("reduction of ",reduces," time unit is possible")
                    #print("count :: ",count)
                    self.timings[i] -= min(reduces, current_unit - 1)
                    Tasks_Timings[int(task)] += ( min(reduces, current_unit - 1)  * (16/effic) ) 
                    #print("new unit :: ",self.timings[i]," and new time",Tasks_Timings[int(task)],"\n")

    def insert_in_schedule(self, task, maximum):
        t = get_alias(str(task), self.ID)
        min_bid = float('inf')
        ins = -1
        old_max = maximum
        for index in range(len(self.schedule)):
            alias = get_alias(str(self.schedule[index]), self.ID)
            prelim = BFSR(alias,t,1)
            if index + 1 != len(self.schedule):
                alias1 = get_alias(str(self.schedule[index+1]), self.ID)
            if t != self.schedule[index]:
                if index < len(self.schedule) - 1 and prelim[-1] in Data.ADJ[alias1]:
                    bid = len(prelim) - 2 + min(round(1/Data.expl[(self.ID,t,task)]), math.ceil(Tasks_Timings[int(task)] / (16 * Data.expl[(self.ID,t,task)])),math.ceil(Tasks_Timings[int(task)])) + sum(self.timings)

                elif index == len(self.schedule)-1:
                    bid = len(prelim) - 2 + min(round(1/Data.expl[(self.ID,t,task)]), math.ceil(Tasks_Timings[int(task)] / (16 * Data.expl[(self.ID,t,task)])),math.ceil(Tasks_Timings[int(task)])) + sum(self.timings)
                else:
                    bid = float('inf')
            else:
                bid = float('inf')
            if bid < maximum:
                min_bid = bid
                maximum = min_bid
                ins = index + 1
        if ins != -1:
            alias = get_alias(str(self.schedule[ins-1]) , self.ID )
            paths = BFSR(alias,t,1)
            path = []
            for p in paths:
                path.append(int(p) %len(Data.CELLS))
            del path[0]
            self.schedule = self.schedule[:ins] + path + self.schedule[ins : ]

        # ADDING THE TIMING
            aliass = str(get_alias(str(task),self.ID))
            effic = round(1/Data.expl[(self.ID,aliass,str(task))])
            # Maximum is the reduced value after removing the task
            diff = old_max - sum(self.timings)

            unit = min(4, diff, int(Tasks_Timings[int(task)]))
            if path == []:
                self.timings[self.schedule.index(int(task))] += unit
            done = (16/effic) * unit
            
            for i in range(len(path) - 1):
                aliass = str(get_alias(str(path[i]),self.ID))
                effic = round(1/Data.expl[(self.ID,aliass,str(path[i]))])
                dones = (16/effic)
                Tasks_Timings[int(path[i])] -= dones
            if path != []:
                self.timings = self.timings[:ins] + [1] * (len(path) - 1) + [unit] + self.timings[ins :]
            Tasks_Timings[int(task)] -= done

# Assign task to each of the agents
def Assign_tasks_to_agents(All_Tasks, bidding, work, sch, time, pa):
    global AGENT_OBJ, Visited, Tasks_Timings
    BIDDERS = AGENT_OBJ.copy()

    for k in range(len(All_Tasks)):
        for ag in AGENT_OBJ:
            if sum(ag.won) >= ((threshold + 8) % 4 + threshold + 8)/4:
                if ag in BIDDERS:
                    BIDDERS.remove(ag)
        
        if len(BIDDERS) == 0:
            break
        
        # Holds the bids for each agent
        current_bid = []

        #print(All_Tasks)
        for ag in BIDDERS:
            
            mini = float("inf")
            for task in All_Tasks:
                bid = ag.Generate_bid(task, bidding, work, sch, time, pa,2)

                if bid < mini:
                    mini = bid
                    best = task
                if bid == mini:
                    if int(task) > int(best):
                        best = task
    
            
            ag.bid = mini
            current_bid.append((mini,best,ag))
        
        # Getting the minimum bid 
        min_bid = min([x[0] for x in current_bid])
        #print(task, current_bid)
        
        # Getting the list of all agents that have the minimum bid
        Robot = []
        for ag in current_bid:
            if ag[0] == min_bid:
                
                task = ag[1]
                if task in All_Tasks:
                    All_Tasks.remove(task)
                
                Robot.append(ag[2])
                ag[2].won.append(1)
                break
        
        
        # Assigning the tasks to each robot with the minimum bid
        for ag in Robot:
            
            path = BFSR(ag.initial_loc, get_alias(task, ag.ID) , 1)
            #print(task)
            #ag.won.append(  int(task))
            if len(path) > 1:
                path = path[1:]
            
            for i in range(len(path)):
                elem = path[i] 
                ag.schedule.append(int(elem)%len(Data.CELLS))
                taskss = int( elem) % len(Data.CELLS)
                effic = round(1/Data.expl[(ag.ID, elem,str(taskss))])
                if i != len(path)-1:
                    unit = 1
                    done = (16/effic)
                    Tasks_Timings[taskss] -= done
                    ag.timings.append(unit)
                else:
                   
                    
                    unit = max(math.ceil(Tasks_Timings[taskss] / (16* Data.expl[(ag.ID, elem,str(taskss))])),1)
                    ag.timings.append(unit)
    
                    done = (16/effic) * unit
                    Tasks_Timings[taskss] -= done

            ag.initial_loc = get_alias(str(ag.schedule[-1]),ag.ID)    

def get_agents(task):
    co = []
    for ag in AGENT_OBJ:
        co.append(ag.search_for_tasks(task))
    return sum(co)

def get_efficacy(task):
    efficacy = []
    for ag in AGENT_OBJ:
        efficacy.append(ag.get_task_efficacy(task))
    
    count = efficacy.count("nope")
    while count != 0:
        efficacy.remove("nope")
        count -= 1
    return efficacy.count(4)

def Assign_timings_to_agents():
    for ag in AGENT_OBJ:
        for task in ag.schedule:
            
            #if Tasks_Timings[task] <= 0:
            alias = str(get_alias(str(task),ag.ID))
            #task_count = get_agents(task)
            optimal = get_efficacy(task)
            effic = round(1/Data.expl[(ag.ID,alias,str(task))]) 
            count = ag.schedule.count(task)
             
            if effic == 4:  
                unit = math.ceil(effic/optimal)
                unit = round(unit/count)
                if unit == 0:
                    unit = 1
                #if unit == 0:
                    #print("wut", effic/optimal,math.ceil(effic/optimal),count )
            else:
                unit = 1
            if optimal == 0 and effic == 8:
                unit = 2
            #if unit == 0:
                #print("zero found in ag ",ag.ID," task ", task," effic " , effic," count ", count," optimla", optimal, " left ",Tasks_Timings[task])
            
            '''LATEST MODIFICATION : Addition of the if statement and making unit = 1 if task is already done'''
            if Tasks_Timings[task] > 0:
                ag.timings.append(unit)
                done = (16/effic) * unit
                Tasks_Timings[int(task)] -= done
            else:
                unit = 1
                ag.timings.append(unit)
                done = (16/effic) * unit
                Tasks_Timings[int(task)] -= done

def get_task_left():
    Tasks_Left = []
    for i in range(len(Tasks_Timings)):
        if Tasks_Timings[i] > 0:
            Tasks_Left.append(i)
    return Tasks_Left

def get_index(task, ag):
    index = []
    for i in range(len(ag.schedule)):
        if ag.schedule[i] == task:
            index.append(int(i))
    return index

def update_timings(indices, ag, diff, task, Tasks_Timings):
    if Tasks_Timings[task] <= 0:
        return
    alias = str(get_alias(str(task),ag.ID))
    effic = round(1/Data.expl[(ag.ID,alias,str(task))]) 
    unit = min(diff, round(Tasks_Timings[task] / (16 * Data.expl[(ag.ID,alias,str(task))])  )  )
    done = (16/effic) * (unit)
    #print("time left before mod :: ",sum(ag.timings))
    #print("Task time left before mod", Tasks_Timings[task])
    #print(effic,Tasks_Timings[task] / (16 * Data.expl[(ag.ID,alias,str(task))])   , math.ceil(Tasks_Timings[task] / (16 * Data.expl[(ag.ID,alias,str(task))])  ) )
    for index in indices:
        ag.timings[index] += unit
        Tasks_Timings[task] -= done
    #print("task :: ", task, " tasks left after mod :: ", Tasks_Timings[task], " time invested :: ", done)
    #print("unit :: ",unit ," done :: ",done, " new timings :: ", sum(ag.timings),"\n")

def Change_inschedule_task_timings(ag, Tasks_Left, Tasks_Timings,current_maximum):
    #stores the list of left tasks if present in schedule
    difference = current_maximum - sum(ag.timings)
    left_task_present = []
    
    for i in range(len(ag.schedule)):
        if ag.schedule[i] in Tasks_Left:
            left_task_present.append(ag.schedule[i])

    overlap = []
    task_time = []
    if len(left_task_present) != 0:
        for t in left_task_present:
            overlap.append((Tasks_Timings[int(t)],t))
            task_time.append(int(Tasks_Timings[int(t)]))
        overlap.sort()
        
        diff = math.floor(difference/1)
        if len(overlap) != 0:
            elem = overlap[0]
            task = elem[1]
            indices = get_index(task,ag)
            alias = str(get_alias(str(task),ag.ID))
            effic = round(1/Data.expl[(ag.ID,alias,str(task))]) 
            while diff != 0:
                unit = 1
                done = (16/effic) * (unit)
                ag.timings[int(indices[0])] += 1
                Tasks_Timings[int(task)] -= done
                diff -= 1
                if Tasks_Timings[int(task)] <= 0:
                    break

def sort_agents():
    output = []
    times  = []
    max_agents = []
    for ag in AGENT_OBJ:
        times.append(sum(ag.timings))
    times.sort()
    maximum = max(times)
    for t in times:
        for ag in AGENT_OBJ:
            if maximum == sum(ag.timings) and ag not in max_agents:
                max_agents.append(ag)
            if t == sum(ag.timings) and (ag not in output) and sum(ag.timings) != maximum:
                output.append(ag)

    return output,max_agents,maximum

def get_max():
    times = []
    for ag in AGENT_OBJ:
        times.append(sum(ag.timings))
    
    return max(times)


def get_weights(array):
    work,sch,time,path = 1,1,1,1
    work = float(array[0])
    sch = float(array[1])
    time = float(array[2])
    path = float(array[3])
    return work,sch,time,path


def assign_tasks_to_1():
    ag = AGENT_OBJ[0]
    size = len(Data.CELLS)

    path = BFSR(ag.initial_loc,get_alias('0',ag.ID),1)
    if len(path) > 1:
        path = path[1:]
    ag.schedule = [int(x) % size for x in path]
    ag.timings = [1] * (len(path) - 1) + [round(1/Data.expl[(ag.ID,get_alias('0',ag.ID),str(0))])]

    work = []
    rowlen = int(math.sqrt(size))
    k = 0
    for i in range(0,size,rowlen):
        row = range(i,i+rowlen)
        if k % 2 == 0:
            work += row
        else:
            work += reversed(row)

        k += 1

    work = work[1:]
    plan_time = []

    for t in work:
        effic = round(Tasks_Timings[int(t)] /   (16 *  Data.expl[(ag.ID,get_alias(str(t),ag.ID),str(t))])   )
        if t in ag.schedule:
            effic -= 1
        plan_time += [effic]
    
    ag.schedule += work
    ag.timings += plan_time

def assign_tasks_to_1_2():
    ag = AGENT_OBJ[0]
    size = len(Data.CELLS)

    rounds = len(All_Tasks)
    for index in range(rounds):


        if All_Tasks == []:
            break
    
        s = float("inf")
        best = All_Tasks[0]
        for task in All_Tasks:
            path = BFSR(ag.initial_loc,get_alias(task,ag.ID),1)
            if len(path) > 1:
                path = path[1:]
            if len(path) < s:
                s = len(path)
                best = task
        
        if best in All_Tasks:
            All_Tasks.remove(best)
        
        final = BFSR(ag.initial_loc,get_alias(best,ag.ID),1)
        if len(final) > 1:
            final = final[1:]
        final = [int(x) % size for x in final]
        newtim = [1] * (len(final) - 1)
        newtim += [max(round(Tasks_Timings[int(best)] /   (16 *  Data.expl[(ag.ID,get_alias(str(best),ag.ID),str(best))])),1)]

        for t1 in range(len(final)):
            Tasks_Timings[final[t1]] -= newtim[t1] * round(Data.expl[(ag.ID,get_alias(str(final[t1]),ag.ID),str(final[t1]))] * 16)
        
        ag.schedule += final
        ag.timings += newtim

        for check in range(len(Tasks_Timings)):
            if Tasks_Timings[check] <= 0:
                Tasks_Completed[check] = True
                if str(check) in All_Tasks:
                    All_Tasks.remove(str(check))
        
        ag.initial_loc = get_alias(str(ag.schedule[-1]),ag.ID)


def coor(task):
    size = len(Data.CELLS)
    task = int(task) % size
    x,y = task % int(math.sqrt(size)), task // int(math.sqrt(size))
    return x,y

def coor2task(x,y):
    size = len(Data.CELLS)
    num = int(math.sqrt(size))
    return y * num + x

def get_meeting_point():
    AGENTSS = [x for x in AGENT_OBJ if len(x.schedule) > 0]
    x,y = coor(AGENTSS[0].schedule[-1])
    ans = []
    for ag in AGENTSS:
        x1,y1 = coor(ag.schedule[-1])
        ans.append((x1-x,y1-y))
    
    x2= round(sum([x[0] for x in ans]) / len(AGENTSS)) + x
    y2 = round(sum([x[1] for x in ans]) / len(AGENTSS)) + y

    return coor2task(x2,y2)





if __name__ == "__main__":
    usage = "usage: %prog [options] mdata"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()
    #print(args, len(args))
    if len(args) not in [6,7,9]:
        print("Invalid number of arguments")
        sys.exit(0)

    # args[0] == INSTANCE NAME
    # args[1] == GROUPS
    # args[2] == AGENT LOCATIONS
    # args[3] == THRESHOLD
    # args[4] == meetup/nomeetup
    # args[5] == Tasks covergage list
    # OPTIONAL : meeting point
    # OPTIONAL: STAR/NO STAR
    # OPTIONAL : Network Distance

    Data.readMDATA(args[0])
    
    ''' HARDCODED '''
    numb_agents = 10
    #print(numb_agents)

    if (len(args) in [6,7,9]) and (args[4] == "meetup" or args[4] == "nomeetup"):
        Data.A = [x for x in args[1].split("-")]
        locs = [x for x in args[2].split("-")]
        if args[4] == "meetup":
            meetup = True
        else:
            meetup = False
        threshold = int(args[3]) - 8
    else:
        print("INVALID VALUE/NUMBER OF BIDDING ARGUMENT".lower())
        sys.exit(0)

    if args[4] == "nomeetup":
        meetup = False
    
    if len(args) == 9:
        if args[7] not in ["star","nostar"]:
            print("INVALID ARGUMENT FOR STAR TOPOLOGY".lower())
            sys.exit(0)

    All_Tasks = [x for x in Data.CELLS]
    #print(All_Tasks)
    #print(All_Tasks)
    
    randomize = False
    if randomize:
        random.shuffle(All_Tasks)
    #print(All_Tasks)
    Tasks_Completed = [False] * len(Data.CELLS)
    Visited = [False] * len(Data.CELLS)
    #Tasks_Timings = [16] * len(Data.CELLS)

    Tasks_Timings = [round(float(x) * 16) for x in args[5].split("-")]

    for i in range(len(Tasks_Timings)):
        if Tasks_Timings[i] <= 0:
            Tasks_Completed[i] = True
            if str(i) in All_Tasks:
                All_Tasks.remove(str(i))
    
    
    #print(All_Tasks)
    randomize = False
    if randomize:
        random.shuffle(All_Tasks)
    #print(All_Tasks)
    Tasks_Completed = [False] * len(Data.CELLS)
    Visited = [False] * len(Data.CELLS)
    #Tasks_Timings = [16] * len(Data.CELLS)

    Bfs_Ans = {}

    All_Agents = Data.A
    for agent in All_Agents:
        AGENT_OBJ.append(agent_info(agent))
    randomize = False
    bidding = False
    if bidding != True:
        work = 1
        sch = 1
        path = 1
        time = 1 
    else:
        work,sch,time,path = get_weights(args[3:])

    start = TI.time()
    k = 0
    for ag in AGENT_OBJ:
        ag.initial_loc = get_alias(str(locs[k]),ag.ID)
        k += 1

    if len(AGENT_OBJ) > 1:
        Assign_tasks_to_agents(All_Tasks, bidding, work, sch, time, path)
    else:
        assign_tasks_to_1_2()
        if meetup == True:
            for ag in AGENT_OBJ:
                accum = 0
                index = 0
                for times in ag.timings:
                    if accum < int(threshold):
                        accum += int(times)
                        index += 1
                    else:
                        break
                diff = abs(accum - int(threshold))

                ag.schedule = ag.schedule[:index]
                ag.timings = ag.timings[:index]
                if sum(ag.timings) > int(threshold) and ag.timings != []:
                    temp_time  = int(ag.timings[-1]) - diff
                    ag.timings[-1] = (temp_time)
        
        for ag in AGENT_OBJ:
            print(ag.ID)
            for i in range(len(ag.schedule)):
                task = get_alias(str(ag.schedule[i]), str(ag.ID))
                ag.schedule[i] = int(task)

            print(ag.schedule)
            print(ag.timings)
            
            sys.exit(0)
    if len(Data.A) > 1:
        
        Tasks_Timings = [round(float(x) * 16) for x in args[5].split("-")]
        for ag in AGENT_OBJ:
            ag.timings = []
        Assign_timings_to_agents()
        time = []
        for ag in AGENT_OBJ:
            time.append(sum(ag.timings))

        count = 0
        for elem in Tasks_Timings:
            if elem < -4:
                count += 1

        current_maximum = max(time)

        #print(current_maximum, get_task_left())
        
        for ag in AGENT_OBJ:
            if sum(ag.timings) == current_maximum:
                ag.reset_agent_overkill()

        
        test2 = []
        for i in range(20):
            
            for ag in AGENT_OBJ:
                Tasks_Left = get_task_left()
                Change_inschedule_task_timings(ag, Tasks_Left, Tasks_Timings, math.ceil(current_maximum * 2) )
                test2.append(sum(ag.timings))
        
        
        for i in range(len(All_Agents)):
            s =[] 
            for ag in AGENT_OBJ:
                s.append(sum(ag.timings))
            for ag in AGENT_OBJ:
                if sum(ag.timings) == max(s):
                    ag.reset_agent_overkill()  

        #
        
        #print("Time checker test 1 ::::::: " + str([x < 0.0601 for x in TIMES2] == [True] * len(Data.CELLS))+"\n")
        #print(":::::::::::::::::Agents timing checker ::::::: \n")
        
        # IT IS CORRECT
        
        iteration = True
        for i in range(len(Data.A)-1):
            Agents,max_agents,maximum = sort_agents()
            #print(maximum)
            for max_ag in max_agents:
                count = 0
                if iteration:
                    #print(max_ag.ID, max_ag.schedule)
                    for ind in range(len(max_ag.schedule)):
                        #optimal = get_efficacy(max_ag.schedule[ind])
                    
                        if max_ag.timings[ind] > 4:
                            #print(max_ag.ID, max_ag.schedule[ind])
                            count += 1
                            alias = str(get_alias(str(max_ag.schedule[ind]),max_ag.ID))
                            effic = round(1/Data.expl[(max_ag.ID,alias,str(max_ag.schedule[ind]))])
                            Tasks_Timings[max_ag.schedule[ind]] += (16/effic) * (max_ag.timings[ind] - 1)
                            
                            prev = max_ag.timings[ind]
                            max_ag.timings[ind] = 1

                            for ag in Agents:
                                #print("TASK TO INSERT ",max_ag.schedule[ind])
                                #print(ag.ID, "BEFORE ::: ",ag.schedule, len(ag.schedule)," old sum :: ", sum(ag.timings))
                                if Tasks_Timings[int(max_ag.schedule[ind])] > 0:
                                    ag.insert_in_schedule(str(max_ag.schedule[ind]), maximum)
                                #print("AFTER ::: ",ag.schedule, len(ag.schedule),"new sum :: ",sum(ag.timings),"\n")

                            
                            #print(max_ag.timings[ind],Tasks_Timings[int(max_ag.schedule[ind])])
                            if Tasks_Timings[int(max_ag.schedule[ind])] > 0:
                                
                                max_ag.timings[ind] = prev
                                Tasks_Timings[int(max_ag.schedule[ind])] -= (16/effic) * (prev-1)
                                count -= 1
                                #print(max_ag.timings[ind],Tasks_Timings[int(max_ag.schedule[ind])])
                                continue

                            if count > 0:
                                break

        Agents,max_agents,maximum = sort_agents()
        times = []
        #print(" AFTER LINEAR REDUCTION ")  
        for ag in AGENT_OBJ:
            #print(ag.ID, ag.timings,sum(ag.timings))
            times.append(sum(ag.timings))
        #print(" MAXIMUM ::::::::: ", get_max())
        
        for ag in AGENT_OBJ:
                if sum(ag.timings) == get_max():
                    ag.reset_agent_overkill() 

        for i in range(20):
            
            for ag in AGENT_OBJ:
                Tasks_Left = get_task_left()
                Change_inschedule_task_timings(ag, Tasks_Left, Tasks_Timings, math.ceil(max(times) * 100))
                test2.append(sum(ag.timings))

        ##print(" MAXIMUM ::::::::: ", get_max())
        #print("TASK LEFT ::::: ", get_task_left(), len(get_task_left()))


        # IT IS CORRECT
        
        iteration = True
        for i in range(len(Data.A)-1):
            Agents,max_agents,maximum = sort_agents()
            #print(maximum)
            for max_ag in max_agents:
                count = 0
                if iteration:
                    #print(max_ag.ID, max_ag.schedule)
                    for ind in range(len(max_ag.schedule)):
                        #optimal = get_efficacy(max_ag.schedule[ind])
                    
                        if max_ag.timings[ind] > 4:
                            #print(max_ag.ID, max_ag.schedule[ind])
                            count += 1
                            alias = str(get_alias(str(max_ag.schedule[ind]),max_ag.ID))
                            effic = round(1/Data.expl[(max_ag.ID,alias,str(max_ag.schedule[ind]))])
                            Tasks_Timings[max_ag.schedule[ind]] += (16/effic) * (max_ag.timings[ind] - 1)
                            
                            prev = max_ag.timings[ind]
                            max_ag.timings[ind] = 1

                            for ag in Agents:
                                #print("TASK TO INSERT ",max_ag.schedule[ind])
                                #print(ag.ID, "BEFORE ::: ",ag.schedule, len(ag.schedule)," old sum :: ", sum(ag.timings))
                                if Tasks_Timings[int(max_ag.schedule[ind])] > 0:
                                    ag.insert_in_schedule(str(max_ag.schedule[ind]), maximum)
                                #print("AFTER ::: ",ag.schedule, len(ag.schedule),"new sum :: ",sum(ag.timings),"\n")

                            
                            #print(max_ag.timings[ind],Tasks_Timings[int(max_ag.schedule[ind])])
                            if Tasks_Timings[int(max_ag.schedule[ind])] > 0:
                                
                                max_ag.timings[ind] = prev
                                Tasks_Timings[int(max_ag.schedule[ind])] -= (16/effic) * (prev-1)
                                count -= 1
                                #print(max_ag.timings[ind],Tasks_Timings[int(max_ag.schedule[ind])])
                                continue

                            if count > 0:
                                break

        if meetup == True:
            size = len(Data.CELLS)
            for ag in AGENT_OBJ:
                accum = 0
                index = 0
                for times in ag.timings:
                    if accum < int(threshold):
                        accum += int(times)
                        index += 1
                    else:
                        break
                diff = abs(accum - int(threshold))

                ag.schedule = ag.schedule[:index]
                ag.timings = ag.timings[:index]
                if sum(ag.timings) > int(threshold) and ag.timings != []:
                    temp_time  = int(ag.timings[-1]) - diff
                    ag.timings[-1] = (temp_time)

            if len(args) == 6:
                point = str(get_meeting_point())
            else:
                point = str(int(args[6]) % len(Data.CELLS))

            if len(args) == 8 or len(args) == 9:
                x,y = coor(point)
                meetingpoints = [point]
                if x - int(args[8]) >= 0 and y - int(args[8]) >= 0:
                    meetingpoints.append(coor2task(x - int(args[8]),y - int(args[8])))
                if x + int(args[8]) < int(math.sqrt(size)) and y + int(args[8]) < int(math.sqrt(size)):
                    meetingpoints.append(coor2task(x + int(args[8]),y + int(args[8])))
                if x - int(args[8]) >= 0  and y + int(args[8]) < int(math.sqrt(size)):
                    meetingpoints.append(coor2task(x - int(args[8]),y + int(args[8])))
                if x + int(args[8]) < int(math.sqrt(size)) and y - int(args[8]) >= 0:
                    meetingpoints.append(coor2task(x + int(args[8]),y - int(args[8])))
            
            

                if len(AGENT_OBJ[0].schedule) > 0:
                    path = BFSR(get_alias(str(AGENT_OBJ[0].schedule[-1]),AGENT_OBJ[0].ID),get_alias(point,AGENT_OBJ[0].ID),1)
                else:
                    path = BFSR(AGENT_OBJ[0].initial_loc,get_alias(point,AGENT_OBJ[0].ID),1)
                if len(path) > 1:
                    path = path[1:]
                path = [int(x) % size for x in path]
                AGENT_OBJ[0].schedule += path
                AGENT_OBJ[0].timings += [1] * len(path)

                randint = random.randint(0, len(meetingpoints)-1)

                for ag in AGENT_OBJ[1:]:
                    if len(ag.schedule) > 0:
                        point1 = get_alias(str(ag.schedule[-1]),ag.ID)
                        point2 = get_alias(str(meetingpoints[randint]),ag.ID)
                        path = BFSR(point1,point2,1)
                    else:
                        path = BFSR(ag.initial_loc,get_alias(str(meetingpoints[randint]),ag.ID),1)
                    if len(path) > 1:
                        path = path[1:]
                    path = [int(x) % size for x in path]
                    ag.schedule += path
                    ag.timings += [1] * len(path)

                    randint = (randint + 1) % len(meetingpoints)
            
            else:

                for ag in AGENT_OBJ:
                    if len(ag.schedule) > 0:
                        path = BFSR(get_alias(str(ag.schedule[-1]),ag.ID),get_alias(point,ag.ID),1)
                    else:
                        path = BFSR(ag.initial_loc,get_alias(point,ag.ID),1)
                    if len(path) > 1:
                        path = path[1:]
                    path = [int(x) % size for x in path]
                    ag.schedule += path
                    ag.timings += [1] * len(path)
    

    for ag in AGENT_OBJ:
        
        for i in range(len(ag.schedule)):
            task = get_alias(str(ag.schedule[i]), str(ag.ID))
            ag.schedule[i] = int(task)
        
        if len(ag.schedule) > 0:
            print(ag.ID)
            print(ag.schedule)
            print(ag.timings)

    #print(Tasks_Timings)
    #print(get_task_left)
    '''
    
    TIMES2 = [16] * len(Data.CELLS)
    for ag in AGENT_OBJ:
        for t in range(len(ag.schedule)):
            TIMES2[int(ag.schedule[t])%len(Data.CELLS)] -= round(Data.expl[(ag.ID,ag.locs[int(ag.schedule[t])],str(int(ag.schedule[t])%len(Data.CELLS)))] * 16 * ag.timings[t])
    
    #print("Time checker test 2 ::::::: " + str([x < 0.0601 for x in TIMES2] == [True] * len(Data.CELLS))+"\n")
    #print(":::::::::::::::::Agents timing checker ::::::: \n")
    ans = []
    for ag in AGENT_OBJ:
        ans.append([x > 0 for x in ag.timings] == [True] * len(ag.timings))
    print(str(ans == [True] * len(AGENT_OBJ)), end = " ")


    TIMES2 = [16] * len(Data.CELLS)
    for ag in AGENT_OBJ:
        for t in range(len(ag.schedule)):
            TIMES2[int(ag.schedule[t])%len(Data.CELLS)] -= round(Data.expl[(ag.ID,ag.locs[int(ag.schedule[t])],str(int(ag.schedule[t])%len(Data.CELLS)))] * 16 * ag.timings[t])
    
    #print("Time checker test 2 ::::::: " + str([x < 0.0601 for x in TIMES2] == [True] * len(Data.CELLS))+"\n")
    #print(":::::::::::::::::Agents timing checker ::::::: \n")
    ans = []
    for ag in AGENT_OBJ:
        ans.append([x > 0 for x in ag.timings] == [True] * len(ag.timings))
    print(str((ans == [True] * len(AGENT_OBJ)) and ([x < 0.0601 for x in TIMES2] == [True] * len(Data.CELLS))), end = " ")
    with open("OUTPUT_FILES/" + args[0].replace(".mdata","") + str(".out"),"w") as output:



        for ag in AGENT_OBJ:
            output.write(ag.ID + "\n")
            output.write(str(ag.schedule)+ "\n")
            output.write(str(ag.timings)+ "\n")
        
    #print(TIMES2)

    print(get_max())
    #print(TIMES2)
    end = TI.time()
    print("TIME in seconds : " + str(end-start))
    print("TIME in minutes : " + str(round((end-start)/60)))
    '''
   