import matplotlib.pyplot as plt
import sys
import math
import os
FILE = open(str(sys.argv[1]),"r")
All = []
for lines in FILE:
    l = lines[4:len(lines)-1].split(",")
    l = [int(x)+171 for x in l]
    All.append(l)
    print(l)

padd = len(All)*[0]
Final = []
i = len(All[0]) - 1
while(i > -1):
    temp =  []
    for e in All:
        temp.append(e[i])
    i -= 1
    Final.append(temp)
Final = Final[::-1]
print(Final)
y_lable = ["4","6","8","10","12","14","16"]
y_lable = [int(x) for x in y_lable]
colors = ["r","blue","orange","purple","g","m"]
markers = ["o","v","h","*","p","^"]

l = ["15 interval","25 interval","35 interval","Incremental","centralized"]
for e in range(len(All)):
    plt.plot(y_lable,All[e], linestyle='dotted', marker=markers[e],linewidth = 2,color = colors[e],ms = 7.0,label = l[e])
plt.grid(linestyle = '--', linewidth = 0.5)
plt.legend()
plt.ylabel("Estimated computation time")
plt.xlabel("Number of agents")
plt.show()