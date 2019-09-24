from coordinates import ecef2geodetic, geodetic2ecef
import numpy as np
import seaborn as sns
from astro_dog import AstroDog
from datetime import datetime
from gps_time import GPSTime
import raw_gnss as raw
import helpers as helpers

dog = AstroDog()
time = GPSTime.from_datetime(datetime(2018,1,7))

# We use RINEX3 PRNs to identify satellites
#sat_prn = 'G07'
#sat_pos, sat_vel, sat_clock_err, sat_clock_drift = dog.get_sat_info(sat_prn, time)
#print "Sattelite's position in ecef(m) : \n", sat_pos, '\n'
#print "Sattelite's velocity in ecef(m/s) : \n", sat_vel, '\n'
#print "Sattelite's clock error(s) : \n", sat_clock_err, '\n\n'
#
# we can also get the pseudorange delay (tropo delay + iono delay + DCB correction)
# in the San Francisco area
#receiver_position = [-2702584.60036925, -4325039.45362552,  3817393.16034817]
#delay = dog.get_delay(sat_prn, time, receiver_position)
#print "Sattelite's delay correction (m) in San Fransisco \n", delay




# this example data is the from the example segment
# of the comma2k19 dataset (research.comma.ai)

# example data contains an array of raw GNSS observables
# that were recorded during a minute of highway driving of
# a car, this array format can be used to create Laika's
# GNSSMeasurent object which can be processed with astrodog
# to then be analysed or used for position estimated.
with open('raw_gnss_ublox/value', 'rb') as f:
    f.seek(0)
    example_data = np.load(f)


measurements = [raw.normal_meas_from_array(m_arr) for m_arr in example_data]

# lets limit this to GPS sattelite for the sake of simplicity
measurements = [m for m in measurements if helpers.get_constellation(m.prn) == 'GPS']
print(measurements[0].observables)

# we organize the measurements by epoch and by sattelite for easy plotting
measurements_by_epoch = raw.group_measurements_by_epoch(measurements)
measurements_by_sattelite = raw.group_measurements_by_sat(measurements)

pos_solutions, vel_solutions = [], []
corrected_measurements_by_epoch = []
for meas_epoch in measurements_by_epoch[::10]:
  processed = raw.process_measurements(meas_epoch, dog)
  est_pos = raw.calc_pos_fix(processed)[0][:3]
  corrected = raw.correct_measurements(meas_epoch, est_pos, dog)
  corrected_measurements_by_epoch.append(corrected)
  pos_solutions.append(raw.calc_pos_fix(corrected))
  # you need an estimate position to calculate a velocity fix
  vel_solutions.append(raw.calc_vel_fix(corrected, pos_solutions[-1][0]))
print(pos_solutions)