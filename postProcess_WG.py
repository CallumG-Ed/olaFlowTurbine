import os
import re
import numpy as np
import pandas as pd

def natsort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]
def main():
    waterZ = 2
    
    files = list(filter(lambda a: 'Gauge' in a, os.listdir("postProcessing/")))
    files.sort()
    time_steps = os.listdir("postProcessing/"+files[0]+"/")
    time_steps = sorted(time_steps, key=natsort_key)
    
    string = ''
    for file in files:
        string = string + file + ","
    
    with open('WG_Results.csv', 'w') as f:
        f.write('time,'+string[:-1]+'\n')
    
    with open('WG_Results.csv', 'a') as f:  
        for j, time_step in enumerate(time_steps):
            line = time_step
            for i, file in enumerate(files):
                data = np.array(pd.read_csv("postProcessing/"+file+"/"+time_step+"/data_alpha.water.xy",  header=None, sep=' '))
                data = data[data[:,1]>0.5]
                line = line + ',' + '{:.5f}'.format(data[-1,0] - waterZ)
            f.write(line+'\n')

if __name__ == "__main__":
    main()
