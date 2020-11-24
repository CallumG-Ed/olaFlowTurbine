import os 

lst_dir = os.listdir('.')

for file in lst_dir:
    if file[-4:] != '.dat':
        lst_dir.remove(file)

lst_dir.sort(key = lambda x: x.split('roR')[1])

# lst_dir[lst_dir.find('roR'):]