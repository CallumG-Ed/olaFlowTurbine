import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def NearestVal(array, value):

    array = np.asarray(array)
    idx   = (np.abs(array - value)).argmin()
    return array[idx], idx


def getTurbineVars():

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

    with open('system/fvOptions', 'r') as f:
        for line in f:
            if 'rotorRadius' in line:
                hub_rad = float(line.split()[1][:-1])


    return t, Az, Cp, blade_l, hub_x, hub_y, hub_z, hub_rad


def getElementFiles():

    files = os.listdir('postProcessing/actuatorLineElements/0/')

    if any('blade3' in mystring for mystring in files) == True:
        blades = 3
    else:
        blades = 2
    return files, blades


def transform(angle, F_g):

    '''
    F_b = A * F_g

    where F_b is the transformed force vector vector, F_g the global force vector
    and A_1 and A_2 transformation matrices.


    A_2 = [ 1       0               0       ] <-- this transforms from global
          | 0   cos(Azimuth)   sin(Azimuth) |     to local blade
          [ 0  -sin(Azimuth)   cos(Azimuth) ]

    '''

    angle = angle * math.pi/180

    x = F_g[0]
    y = F_g[1]*math.cos(angle) + F_g[2]*math.sin(angle)
    z = F_g[2]*math.cos(angle) - F_g[1]*math.sin(angle)


    return x, y, z


def sumResults(t,Az,num_blades,files):

    t = np.array(t)
    Az = np.array(Az)

    results = np.zeros((len(t), (num_blades*6)+2))
    results[:,0] = t
    results[:,1] = Az

    for file in files:

        # identify blade and read in information
        blade = int(file.split('.')[1].replace('blade',''))
        table = pd.read_csv('postProcessing/actuatorLineElements/0/'+file)

        #Not sure I need these
        #root_dist = table.root_dist[0]
        #R = root_dist * blade_l

        # Centre coord system at centre hub
        table.x = table.x - hub_x
        table.y = table.y - hub_y
        table.z = table.y - hub_z

        if blade == 1:
            # Move centre from hub centre to blade root
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


def transformToBlade(results):

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

    # add x', y', z' , fx', fy', fz' to table
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

            f_g = [ results.at[j, ('fx'+str(blade))],results.at[j, ('fy'+str(blade))],results.at[j, ('fz'+str(blade))] ]
            m_g = [ results.at[j, ('mx'+str(blade))],results.at[j, ('my'+str(blade))],results.at[j, ('mz'+str(blade))] ]

            results.at[ j, ('Fx'+str(blade)) ] = transform(angle, f_g)[0]
            results.at[ j, ('Fy'+str(blade)) ] = transform(angle, f_g)[1]
            results.at[ j, ('Fz'+str(blade)) ] = transform(angle, f_g)[2]

            results.at[ j, ('Mx'+str(blade)) ] = transform(angle, m_g)[0]
            results.at[ j, ('My'+str(blade)) ] = transform(angle, m_g)[1]
            results.at[ j, ('Mz'+str(blade)) ] = transform(angle, m_g)[2]

    return results


def writeOutputFile(results):
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


t, Az, Cp, blade_l, hub_x, hub_y, hub_z, hub_rad = getTurbineVars()

plt.figure()
plt.plot(t, Cp)
settle = plt.ginput(2)
plt.close()
start = NearestVal(t, settle[0][0])[1]
end = NearestVal(t, settle[1][0])[1]

files, num_blades = getElementFiles()
results = sumResults(t,Az,num_blades,files)
results = transformToBlade(results)
results = results[start:end]
writeOutputFile(results)
