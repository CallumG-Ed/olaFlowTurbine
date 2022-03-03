import pandas as pd
import matplotlib.pyplot as plt


results = pd.read_csv('Results.csv')

plt.figure()
plt.title('Waves')
plt.plot(results.time, results['Gauge3'], label='gauge1')
plt.plot(results.time, results['Gauge4'], label='gauge2')
plt.plot(results.time, results['Gauge5'], label='gauge3')
plt.legend()

plt.figure()
plt.title('Torque')
plt.plot(results.time, results['Mx1'], label='blade1')
plt.plot(results.time, results['Mx2'], label='blade2')
plt.plot(results.time, results['Mx3'], label='blade3')
plt.plot(results.time, results['summed Mx (Q)'], label='summed Mx')
plt.plot(results.time, results['denormalized Cp'], label='denormalized Cp')
plt.legend()

plt.figure()
plt.title('Thrust')
plt.plot(results.time, results['Fx1'], label='blade1')
plt.plot(results.time, results['Fx2'], label='blade2')
plt.plot(results.time, results['Fx3'], label='blade3')
plt.plot(results.time, results['summed Fx (T)'], label='summed Mx')
plt.plot(results.time, results['denormalized Ct'], label='denormalized Ct')
plt.legend()