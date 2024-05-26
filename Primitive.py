import sys
from optparse import OptionParser
import model_data as Data
import math
import random
import time as time_cheker

AGENT_OBJ = []

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

        tlist = Data.ADJ[current]
        random.shuffle(tlist)
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

    def Generate_bid(self, task): 
        self.bid = 0     
        
        alias = str(get_alias(task,self.ID))
        path =  BFSR(self.initial_loc,alias, 1)
        if len(path) > 1:
            path_length = len(path) - 2
        else:
            # assert(len(path) == 1)
            path_length = 1
        #print(sum(self.timings))
        
        val = len(self.schedule) + min(round(1/Data.expl[(self.ID,alias,str(task))]),math.ceil(Tasks_Timings[int(task)] / (16 * Data.expl[(self.ID,alias,str(task))])))
        val /= (path_length + 1)

        val = round(val)
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
def Assign_tasks_to_agents(All_Tasks):
    global AGENT_OBJ, Visited, Tasks_Timings

    for k in range(len(Data.CELLS)):
        # Holds the bids for each agent
        current_bid = []

        #print(All_Tasks)
        for ag in AGENT_OBJ:
            
            mini = float("inf")
            for task in All_Tasks:
                bid = ag.Generate_bid(task)

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
                All_Tasks.remove(task)
                #print("\n" + str(task))
                Robot.append(ag[2])
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
                    #done = (16/effic)
                    #Tasks_Timings[taskss] -= done
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


if __name__ == "__main__":
    usage = "usage: %prog [options] mdata"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()
    #print(args)
    if len(args) not in [3,7]:
        print("Invalid number of arguments")
        sys.exit(0)
    Data.readMDATA(args[0])
    start = int(round(time_cheker.time()))
    if args[2] == "weight" and len(args) == 7:
        bidding = True
    elif args[2] == "noweight" and len(args) == 3:
        bidding = False
    else:
        print("INVALID VALUE/NUMBER OF BIDDING ARGUMENT".lower())
        sys.exit(0)

    if args[1] == "norand":
        randomize = False
    elif args[1] == "rand":
        randomize = True
    else:
        print("INVALID VALUE/NUMBER OF RANDOMIZING ARGUMENT".lower())
        sys.exit(0)
    
    
    start = int(round(time_cheker.time()))
    

    All_Tasks = [x for x in Data.CELLS]

    Tasks_Completed = [False] * len(Data.CELLS)
    Visited = [False] * len(Data.CELLS)
    Tasks_Timings = [16] * len(Data.CELLS)

    Bfs_Ans = {}

    All_Agents = Data.A[1:]
    for agent in All_Agents:
        AGENT_OBJ.append(agent_info(agent))

    Assign_tasks_to_agents(All_Tasks)
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
    print(str(ans == [True] * len(AGENT_OBJ) and [x < 0.0601 for x in TIMES2] == [True] * len(Data.CELLS)), end = " ")
    '''for ag in AGENT_OBJ:
        print(ag.ID)
        print(ag.schedule)
        print(ag.timings)'''
    #print(TIMES2)
    print(get_max())
    end = int(round(time_cheker.time()))
    print("Time in seconds ::::: ", int(end - start))
    print("Time in minutes ::::: ", round( int(end - start) / 60 ))