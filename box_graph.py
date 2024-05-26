import numpy as np
import matplotlib.pyplot as plt
import sys
import math
import os

np.random.seed(10)
x1 = np.random.normal(70, 25, 200)
x2 = np.random.normal(70, 25, 200)
x3 = np.random.normal(70, 25, 200)
x4 = np.random.normal(70, 25, 200)
x5 = np.random.normal(70, 25, 200)
x6 = np.random.normal(70, 25, 200)

data_to_plot = [x1,x2,x3,x4,x5,x6]

# Create a figure instance
fig = plt.figure(1, figsize=(9, 6))

# Create an axes instance
ax = fig.add_subplot(111)

# lables or x axis 
string1 = "-40 to -45|-45 to -50|-50 to -55|-55 to -60|-60 to -65|-65 to -70"
l = string1.split("|") 
labels = l

# Create the boxplot
bp = ax.boxplot(data_to_plot,labels=labels,showmeans=True,meanline=True,showfliers=False,
boxprops= dict(linewidth=1.5, color='black'), whiskerprops=dict(linestyle='-',linewidth=1.5, color='black'))

'''
Default syntax for color change
for median in bp['medians']:
    median.set(color='#b2df8a', linewidth=2)
'''
# change line width of median
for median in bp['medians']:
    median.set(linewidth=2)

# change line width of mean 
for mean in bp['means']:
    mean.set(linewidth=3)

plt.show()