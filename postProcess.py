import pandas as pd
import numpy as np
#from natsort import natsorted
import os
import re

def NearestVal(array, value):
    array = np.asarray(array)
    idx   = (np.abs(array - value)).argmin()
    return array[idx], idx

def natsort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]

def getVars():

    '''
    function looks inside the turbine file for time [s], Azimuth [deg] and Cp
    vectors first. Next it looks in the elementData file to calculate the blade
    length. It then looks in the setup file to get the coordinates of the hub
    centre in the global coordinate system (for translating later). And finally
    it gets the rotor radius from fvOptions.
    '''

    global time, azimuth, TSR, U, rho, Cp, Ct, blade_l, hub_x, hub_y, hub_z, rot_rad, hub_rad, waterZ

    turbine_data = pd.read_csv('postProcessing/turbines/0/turbine.csv')
    time = np.array(turbine_data.time)
    azimuth = np.array(turbine_data.angle_deg)
    Cp = np.array(turbine_data.cp)
    Ct = np.array(turbine_data.cd)

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
         if 'TSR' in line:
             TSR = float(line.split()[1][:-1])
         if 'U_FS' in line:
             U = float(line.split()[1][:-1])
         if 'rho' in line:
             rho = float(line.split()[1][:-1])
         if 'rotor_R' in line:
            rot_rad = float(line.split()[1][:-1])
            hub_rad = rot_rad - blade_l
         if 'freeSurface' in line:
            waterZ = float(line.split()[1][:-1])

    return

def getElementFiles():

    '''
    This function checks for number of blades by parsing the
    actuatorLineElements directory. Each actuator line file is stamped with a
    blade number (i.e. blade1, blade2, blade3 etc)
    '''

    global element_files, num_blades

    element_files = os.listdir('postProcessing/actuatorLineElements/0/')
    element_files = sorted(element_files, key=natsort_key)

    if any('blade3' in mystring for mystring in element_files) == True:
        num_blades = 3
    else:
        num_blades = 2

    return

def transform(angle, fx, fy, fz):

    '''
    F_b = A * F_g

    where F_b (force at blade root) is the transformed force vector, F_g the
    global force vector and A is the transformation matrix.

    A_2 = [ 1       0               0       ] <-- this transforms from global
          | 0   cos(Azimuth)  -sin(Azimuth) |     to local blade
          [ 0   sin(Azimuth)   cos(Azimuth) ]
    '''

    angle = angle * np.pi/180

    Fx = fx
    Fy = fy*np.cos(angle) - fz*np.sin(angle)
    Fz = fz*np.cos(angle) + fy*np.sin(angle)

    return Fx, Fy, Fz

def calculateBladeResults():

    '''
    This function simply goes into each element file of each blade and sums
    them together. For example all elements in blade1 are added together to give
    a sum of forces along the blade. To sum the moments the global coordinate
    system from turbinesFoam is first moved onto centre hub and then for each
    blade moved to the blade root.
    '''
    results = np.zeros((len(time), (num_blades*8)+2))
    results[:,0] = time
    results[:,1] = azimuth

    for file in element_files:

        blade = int(file.split('.')[1].replace('blade',''))

        data = pd.read_csv('postProcessing/actuatorLineElements/0/'+file)
        root_r = np.array(data.root_dist)*rot_rad

        if blade == 1:

            angle = azimuth

            #Global Forces
            fx = np.array(data.fx)
            fy = np.array(data.fy)
            fz = np.array(data.fz)
            results[:,2] += fx
            results[:,3] += fy
            results[:,4] += fz

            #Blade Forces
            Fx = transform(angle, fx, fy, fz)[0]
            Fy = transform(angle, fx, fy, fz)[1]
            Fz = transform(angle, fx, fy, fz)[2]
            results[:,5] += Fx
            results[:,6] += Fy
            results[:,7] += Fz

            #Root Moments
            results[:,8] += Fy*root_r   # Mx
            results[:,9] += Fx*root_r   # My

        elif blade == 2:

            if num_blades == 3:
                angle = azimuth + 120
            elif num_blades == 2:
                angle = azimuth + 180

            #Global Forces
            fx = np.array(data.fx)
            fy = np.array(data.fy)
            fz = np.array(data.fz)
            results[:,10] += fx
            results[:,11] += fy
            results[:,12] += fz

            #Blade Forces
            Fx = transform(angle, fx, fy, fz)[0]
            Fy = transform(angle, fx, fy, fz)[1]
            Fz = transform(angle, fx, fy, fz)[2]
            results[:,13] += Fx
            results[:,14] += Fy
            results[:,15] += Fz

            #Root Moments
            results[:,16] += Fy*root_r   # Mx
            results[:,17] += Fx*root_r   # My

        elif blade == 3:

            angle = azimuth + 240

            #Global Forces
            fx = np.array(data.fx)
            fy = np.array(data.fy)
            fz = np.array(data.fz)
            results[:,18] += fx
            results[:,19] += fy
            results[:,20] += fz

            #Blade Forces
            Fx = transform(angle, fx, fy, fz)[0]
            Fy = transform(angle, fx, fy, fz)[1]
            Fz = transform(angle, fx, fy, fz)[2]
            results[:,21] += Fx
            results[:,22] += Fy
            results[:,23] += Fz

            #Root Moments
            results[:,24] += Fy*root_r   # Mx
            results[:,25] += Fx*root_r   # My

    cols = ['time', 'azimuth']
    for i in range(num_blades):
        cols.append('fx' + str(i+1))
        cols.append('fy' + str(i+1))
        cols.append('fz' + str(i+1))
        cols.append('Fx' + str(i+1))
        cols.append('Fy' + str(i+1))
        cols.append('Fz' + str(i+1))
        cols.append('Mx' + str(i+1))
        cols.append('My' + str(i+1))

    results = pd.DataFrame(results)
    results.columns = cols

    return results

def sumBladeLoads(results):

    if num_blades == 3:
        Q = np.array(results.Mx1) + np.array(results.Mx2) + np.array(results.Mx3)
        T = np.array(results.fx1) + np.array(results.Fx2) + np.array(results.Fx3)
    if num_blades == 2:
        Q = np.array(results.Mx1) + np.array(results.Mx2)
        T = np.array(results.fx1) + np.array(results.Fx2)

    results = np.array((Q,T)).transpose()
    results = pd.DataFrame(results)
    results.columns = ['summed Mx (Q)', 'summed Fx (T)']

    return results

def calculateTurbineResults():

    # Denormalize turbinesFoam outputs
    A = np.pi*rot_rad**2
    omega = (TSR * U)/rot_rad
    Q = (Cp*0.5*rho*A*U**3)/omega
    T = Ct*0.5*rho*A*U**2
    results = np.array((Q,T))

    results = pd.DataFrame(results).transpose()
    results.columns = ['denormalized Cp', 'denormalized Ct']

    return results

def getGaugeData():
    files = list(filter(lambda a: 'Gauge' in a, os.listdir("postProcessing/")))
    files.sort()

    T  = []
    FS = []

    for file in files:
        time_steps_str = os.listdir("postProcessing/"+file+"/")
        time_steps = []
        for time_step in time_steps_str:
            time_steps.append(float(time_step))
        time_steps.sort()

        for time_step in time_steps:
            t = float(time_step)
            l = []
            a = []
            with open("postProcessing/"+file+"/"+('%f' % time_step).rstrip('0').rstrip('.')+"/data_alpha.water.xy") as f:
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

def writeOutput(results):
    results.to_csv('Results.csv')
    return

def main():

    getVars()
    getElementFiles()
    blade_results = calculateBladeResults()
    summed_blade_results = sumBladeLoads(blade_results)
    turbine_results = calculateTurbineResults()
    wave_results = getGaugeData()

    results = joinResults(blade_results, summed_blade_results)
    results = joinResults(results, turbine_results)
    results = joinResults(results, wave_results)
    writeOutput(results)

    return

if __name__ == "__main__":
    main()
