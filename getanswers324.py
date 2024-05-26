import os
import time
from optparse import OptionParser
def get_cmd(dataset, numOfAgent, interval):
    return (f'INSTANCES/comp_L10-R1-{dataset}_mth_n{numOfAgent}t4-1_s2_tw1000.mdata nomeetup {interval}')

if __name__ == "__main__":
    usage = "usage: %prog [options] mdata"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()
    if len(args) not in [2]:
        print(args, len(args))
        print("Invalid number of arguments")
        sys.exit(0)
    # args[0] == interval
   
    agents = [16,6,8,10,12,14,4]
    dataset = [1,2,3,4,5,6,7,8,9,10]
    count = 0
    agents = [str(x) for x in agents]
    repeat = int(args[1])
    start = int(round(time.time()))
    for count in range(len(dataset)):
        for i in range(len(agents)):
            temp = []
            once = True
            for x in range(repeat):
                
                cmd = "python3 sim_script.py "
                cmd += get_cmd(dataset[count],agents[i],args[0])
                if once:
                    print("working on ", cmd)
                    once = False
                output=os.popen(cmd).read()
                output = str(output).split()
                temp.append(int(output[2]))
                end = int(round(time.time()))
            print(f"Time taken to complete {agents[i]} agent for {dataset[count]} is ::::",round(int(end-start)/60))
            print(f"Answer for {agents[i]} agent for {dataset[count]} dataset is :::: ", min(temp))