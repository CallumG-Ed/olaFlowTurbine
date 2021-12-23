import os
import pandas as pd

def mergeData():
    turbines_dir = 'postProcessing/turbines/'
    elements_dir = 'postProcessing/actuatorLineElements/'
    
    folders = os.listdir(turbines_dir)
    folders.sort()
    
    if len(folders) > 1:
        
        frames = [pd.read_csv(turbines_dir+'0/turbine.csv')]
        for i, folder in enumerate(folders):
            if i > 0:
                frames.append(pd.read_csv(turbines_dir+folder+'/turbine.csv'))
        Data = pd.concat(frames)
        Data.to_csv(turbines_dir+'0/turbine.csv', index=False)
    
        base_files = os.listdir(elements_dir+'0/')
        for i, file in enumerate(base_files):
            base_data = pd.read_csv(elements_dir+'0/'+file)
            frames = [base_data]
            for j, folder in enumerate(folders):
                if folder != '0':
                    frames.append(pd.read_csv(elements_dir+folder+'/'+file))
            Data = pd.concat(frames)
            Data.to_csv('postProcessing/actuatorLineElements/0/'+file, index=False)
    return

if __name__ == "__main__":
    mergeData()
                
    