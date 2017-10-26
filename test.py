import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.style.use('ggplot')



heating = pd.read_csv('data/heating-curve.csv').set_index('t')
cooling = pd.read_csv('data/cooling.csv').set_index('t')
heatingTemps = pd.read_csv('data/heatingTemps.csv').set_index('t')
coolingTemps = pd.read_csv('data/coolingTemps.csv').set_index('t')

def toTemp(v):
    return 525672 / (149 * np.log(v) - 149 * np.log(2.5 - v) + 1764)

heating['T'] = heating.apply(lambda row: toTemp(row['V']), axis=1)
cooling['T'] = cooling.apply(lambda row: toTemp(row['V']), axis=1)

T0 = 305.8
T_max = 308.6876
r_heating = 0.0013
r_cooling = 0.002


def make_system(f, t_end):
    '''
    The system has a blanket (DataFrame), a frequency, a time, and the
    section the blanket is currently on.
    '''
    return pd.Series({'status': pd.DataFrame({'T1': [T0], 'T2': [T0], 'T3': [
        T0], 'T4': [T0]}), 'freq': f, 't': 0, 't_end': t_end, 'current': 0})


def update_func(system, t):
    new = [0,0,0,0]
    for section in np.arange(4):
        if section != system.current:
            new[section] = cool(system.status[system.status.columns[section]][t])
        else:
            new[section] = heat(system.status[system.status.columns[section]][t])
    system.status.loc[t + 1] = new



def run_simulation(system):
    for t in np.arange(system.t_end - 1):
        if t % (system.t_end  // system.freq) == 0:
            if system.current == 3:
                system.current = 0
            else:
                system.current += 1

        update_func(system, t)


def cool(t):
    return t + (-r_cooling * (t - T0))


def heat(t):
    return t + (-r_heating * (t - T_max))

def sweep_fs(f0, f_max, timespan):
    results = pd.DataFrame({"T":[]})
    for f in np.arange(f0, f_max):
        system = make_system(f, timespan)
        run_simulation(system)
        results.loc[f] = system.status.tail(1).sum().sum() / 4
    return results


# system = make_system(1,2000)
# run_simulation(system)
# ax = system.status.T2.plot()
# heatingTemps.plot(ax=ax)
# coolingTemps.plot(ax=ax)
# coolingMod.plot(ax=ax)
ax = sweep_fs(1, 60, 3600).plot()
# ax.legend(['Model Heating', 'Actual Heating', 'Model Cooling', 'Actual Cooling'])
ax.set_title('Frequency Sweep for duration of 1 Hour, Artificially Cool Faster')
ax.set_xlabel('Frequency ($moves/hour$)')
ax.set_ylabel('Final Temperature ($K$)')
ax.legend().set_visible(False)
ax.figure.savefig('sweep.png')
