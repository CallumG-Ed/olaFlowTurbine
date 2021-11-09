import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def NearestVal(array, value):
    array = np.asarray(array)
    idx   = (np.abs(array - value)).argmin()
    return array[idx], idx

def getVars():

    '''
    function looks inside the turbine file for time [s], Azimuth [deg] and Cp
    vectors first. Next it looks in the elementData file to calculate the blade
    length. It then looks in the setup file to get the coordinates of the hub 
    centre in the global coordinate system (for translating later). And finally 
    it gets the rotor radius from fvOptions.
    '''
    
    t  = []
    Az = []
    Cp = []

    with open('postProcessing/turbines/0/turbine.csv', 'r') as f:
        for i, line in enumerate(f):
            if i > 0:
                entries = line.split(',')
                t.append(float(entries[0]))
                Az.append(float(entries[1]))
                Cp.append(float(entries[3]))

    with open('system/elementData', 'r') as f:
        x = []
        for i, line in enumerate(f):
            if i > 1:
                x.append(float(line.split()[1]))
        blade_l = x[-1] - x[0]

    with open('setup', 'r') as f:
     for line in f:
         if 'Hub_x' in line:
            hub_x = float(line.split()[1][:-1])
         if 'Hub_y' in line:
            hub_y = float(line.split()[1][:-1])
         if 'Hub_z' in line:
            hub_z = float(line.split()[1][:-1])
         if 'rotor_R' in line:
            Rotor_rad = float(line.split()[1][:-1])
            hub_rad = Rotor_rad - blade_l
         if 'freeSurface' in line:
            waterZ = float(line.split()[1][:-1])

    # with open('system/fvOptions', 'r') as f:
    #     for line in f:
    #         if 'rotor_R' in line:
    #             Rotor_rad = float(line.split()[1][:-1])
    #             hub_rad = Rotor_rad - blade_l


    return t, Az, Cp, blade_l, hub_x, hub_y, hub_z, hub_rad, waterZ

def getElementFiles():
    
    '''
    This function checks for number of blades by parsing the 
    actuatorLineElements directory. Each actuator line file is stamped with a 
    blade number (i.e. blade1, blade2, blade3 etc)
    '''

    files = os.listdir('postProcessing/actuatorLineElements/0/')

    if any('blade3' in mystring for mystring in files) == True:
        blades = 3
    else:
        blades = 2
    return files, blades

def transform(angle, F_g):

    '''
    F_b = A * F_g

    where F_b (force at blade root) is the transformed force vector, F_g the 
    global force vector and A is the transformation matrix.

    A_2 = [ 1       0               0       ] <-- this transforms from global
          | 0   cos(Azimuth)   sin(Azimuth) |     to local blade
          [ 0  -sin(Azimuth)   cos(Azimuth) ]
    '''

    angle = angle * math.pi/180

    x = F_g[0]
    y = F_g[1]*math.cos(angle) + F_g[2]*math.sin(angle)
    z = F_g[2]*math.cos(angle) - F_g[1]*math.sin(angle)
    
    return x, y, z

def sumTurbineResults(t, Az, num_blades, files, hub_rad, hub_x, hub_y, hub_z):
    
    '''
    This function simply goes into each element file of each blade and sums 
    them together. For example all elements in blade1 are added together to give
    a sum of forces along the blade. To sum the moments the global coordinate 
    system from turbinesFoam is first moved onto centre hub and then for each 
    blade moved to the blade root.
    '''

    t = np.array(t)
    Az = np.array(Az)

    results = np.zeros((len(t), (num_blades*6)+2))
    results[:,0] = t
    results[:,1] = Az

    for file in files:

        # identify blade and read in information
        blade = int(file.split('.')[1].replace('blade',''))
        table = pd.read_csv('postProcessing/actuatorLineElements/0/'+file)

        # Centre coord system at centre hub
        table.x = table.x - hub_x
        table.y = table.y - hub_y
        table.z = table.y - hub_z

        if blade == 1:
            # Move centre from hub to blade root. This is so moments can be 
            # calculated at the blade root.
            table.z = table.z - (hub_rad*np.cos(Az*math.pi/180))
            table.y = table.y + (hub_rad*np.sin(Az*math.pi/180))

            #Forces
            results[:,2] = results[:,2] + table.fx
            results[:,3] = results[:,3] + table.fy
            results[:,4] = results[:,4] + table.fz
            #Moments
            results[:,5] = results[:,5] + (table.fy*table.z) - (table.fz*table.y)
            results[:,6] = results[:,6] + (table.fz*table.x) - (table.fx*table.z)
            results[:,7] = results[:,7] + (table.fx*table.y) - (table.fy*table.x)

        elif blade == 2:

            if num_blades == 3:
                # Move centre from hub centre to blade root
                table.z = table.z - (hub_rad*np.cos((Az+120)*math.pi/180))
                table.y = table.y + (hub_rad*np.sin((Az+120)*math.pi/180))
            elif num_blades == 2:
                # Move centre from hub centre to blade root
                table.z = table.z - (hub_rad*np.cos((Az+180)*math.pi/180))
                table.y = table.y + (hub_rad*np.sin((Az+180)*math.pi/180))

            #Forces
            results[:,8] = results[:,8] + table.fx
            results[:,9] = results[:,9] + table.fy
            results[:,10] = results[:,10] + table.fz
            #Moments
            results[:,11] = results[:,11] + (table.fy*table.z) - (table.fz*table.y)
            results[:,12] = results[:,12] + (table.fz*table.x) - (table.fx*table.z)
            results[:,13] = results[:,13] + (table.fx*table.y) - (table.fy*table.x)

        elif blade == 3:
            # Move centre from hub centre to blade root
            table.z = table.z - (hub_rad*np.cos((Az+240)*math.pi/180))
            table.y = table.y + (hub_rad*np.sin((Az+240)*math.pi/180))

            #Forces
            results[:,14] = results[:,14] + table.fx
            results[:,15] = results[:,15] + table.fy
            results[:,16] = results[:,16] + table.fz
            #Moments
            results[:,17] = results[:,17] + (table.fy*table.z) - (table.fz*table.y)
            results[:,18] = results[:,18] + (table.fz*table.x) - (table.fx*table.z)
            results[:,19] = results[:,19] + (table.fx*table.y) - (table.fy*table.x)

    return results

def transformToBlade(results, num_blades):
    
    '''
    Transforms the forces and moments calculated at the blade root in the 
    global reference frame into the blade local reference frame. Function also 
    outputs everything into a dataframe for writing later. Lower case 
    formatted variables (i.e. fx fy, fz, mz, ...) are global parameters upper 
    caes (i.e. Fx Fy, Fz, Mz, ...) are blade reference frame parameters.
    '''

    cols = ['time', 'azimuth']
    for i in range(num_blades):
        cols.append('fx' + str(i+1))
        cols.append('fy' + str(i+1))
        cols.append('fz' + str(i+1))
        cols.append('mx' + str(i+1))
        cols.append('my' + str(i+1))
        cols.append('mz' + str(i+1))

    results = pd.DataFrame(results)
    results.columns = cols

    # add blade transformed quantities to table
    zero = np.zeros((len(results),1))
    for i in range(num_blades):
        results['Fx'+str(i+1)] = zero
        results['Fy'+str(i+1)] = zero
        results['Fz'+str(i+1)] = zero
        results['Mx'+str(i+1)] = zero
        results['My'+str(i+1)] = zero
        results['Mz'+str(i+1)] = zero

    for i in range(num_blades):
        for j in range(len(results)):

            blade = i+1

            if blade == 1:
                angle = results.at[j, 'azimuth']
            elif blade == 2:
                if num_blades == 3:
                    angle = results.at[j, 'azimuth'] + 120
                elif num_blades == 2:
                    angle = results.at[j, 'azimuth'] + 180
            elif blade == 3:
                angle = results.at[j, 'azimuth'] + 240

            f_g = [ results.at[j, ('fx'+str(blade))], results.at[j, ('fy'+str(blade))], results.at[j, ('fz'+str(blade))] ]
            m_g = [ results.at[j, ('mx'+str(blade))], results.at[j, ('my'+str(blade))], results.at[j, ('mz'+str(blade))] ]

            results.at[ j, ('Fx'+str(blade)) ] = transform(angle, f_g)[0]
            results.at[ j, ('Fy'+str(blade)) ] = transform(angle, f_g)[1]
            results.at[ j, ('Fz'+str(blade)) ] = transform(angle, f_g)[2]

            results.at[ j, ('Mx'+str(blade)) ] = transform(angle, m_g)[0]
            results.at[ j, ('My'+str(blade)) ] = transform(angle, m_g)[1]
            results.at[ j, ('Mz'+str(blade)) ] = transform(angle, m_g)[2]

    return results

def getGaugeDate(waterZ):    
    files = list(filter(lambda a: 'Gauge' in a, os.listdir("postProcessing/")))
    files.sort()
    
    T  = []
    FS = []
    
    for file in files:     
        time_steps = os.listdir("postProcessing/"+file+"/")
        time_steps.sort()
        for time_step in time_steps:
            t = float(time_step)
            l = []
            a = []
            with open("postProcessing/"+file+"/"+time_step+"/data_alpha.water.xy") as f:
                for line in f:
                    l.append(float(line.split()[0]))
                    a.append(float(line.split()[1]))
            data = np.array([l,a]).transpose()
            data = data[data[:,1]>0.5]
            fs   = data[-1,0] - waterZ
            T.append(t)
            FS.append(fs)
    
    steps = int(len(T)/len(files))
    alpha_water = np.zeros((steps,len(files)+1))
    alpha_water[:,0] = T[0:steps]
    for i in range(len(files)):
        alpha_water[:,i+1] = FS[i*steps:i*steps+steps]
    results = pd.DataFrame(alpha_water[:,1:])    
    results.columns = files 
    
    return results

def joinResults(results1, results2):  
    results = results1.join(results2)   
    return results

def writeOutputFile(results):
    
    '''
    Simply writes results dataframe to csv file
    '''
    
    with open('Results.csv', 'w') as f:
        for col in results.columns:
            f.write(col+',')
        f.write('\n')

    rows, cols = results.shape

    with open('Results.csv', 'a') as f:
        for row in range(rows):
            for col in range(cols):
                f.write('{0:.5f}'.format(results.iloc[row,col]) + ',')
            f.write('\n')
    return

def main():
        
    t, Az, Cp, blade_l, hub_x, hub_y, hub_z, hub_rad, waterZ = getVars()
    
    plt.figure()
    plt.plot(t, Cp)
    settle = plt.ginput(2)
    plt.close()
    start = NearestVal(t, settle[0][0])[1]
    end = NearestVal(t, settle[1][0])[1]
    
    files, num_blades = getElementFiles()
    turbine_results = sumTurbineResults(t, Az,num_blades, files, hub_rad, hub_x, hub_y, hub_z)
    turbine_results = transformToBlade(turbine_results, num_blades)
    turbine_results = turbine_results[start:end]
    guage_results = getGaugeDate(waterZ)
    results = joinResults(turbine_results, guage_results)
    writeOutputFile(results)
    
    return

if __name__ == "__main__":
    main()
                

            
        
    
        