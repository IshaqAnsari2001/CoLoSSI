with open("soldata.txt","r") as data:
    info = data.readlines()
    
    data = []
    m = 0
    for i in range(2,len(info),3):
      k = int(info[i][info[i].rindex(":") + 1:])
      data += [k]
      m+= 1
      if m > 0 and m % 7 == 0:
        #print(m)
        dataset = [data[m-1]] + data[m-6:m-1] + [data[m-7]]
        for d in dataset:
            print(d,end=" ")
        print("")
        
        
        