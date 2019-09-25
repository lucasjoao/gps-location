import numpy as np
from astro_dog import AstroDog
from datetime import datetime
from gps_time import GPSTime
import raw_gnss as raw
import helpers as helpers

dog = AstroDog()
time = GPSTime.from_datetime(datetime(2018,1,7))

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
print( 'Exemplo de raw data de um satelite\n'
        + 'C1C = pseudorange\n'
        + 'D1C = doppler\n'
        + 'L1C = carrier phase\n'
        + 'S1C = signal strength\n'
        ,measurements[0].observables)#observables ta no formato rinex

# we organize the measurements by epoch and by sattelite for easy plotting
measurements_by_epoch = raw.group_measurements_by_epoch(measurements) # uma epoch é um instante onde foram obtidas todas as medições dos satelites disponiveis
measurements_by_sattelite = raw.group_measurements_by_sat(measurements)

pos_solutions = []
corrected_measurements_by_epoch = []

for meas_epoch in measurements_by_epoch[::10]: # vai processar 10 instantes
  processed = raw.process_measurements(meas_epoch, dog) # popula dados no objeto
  est_pos = raw.calc_pos_fix(processed)[0][:3] # calcula uma estimativa da posição
  corrected = raw.correct_measurements(meas_epoch, est_pos, dog) # corrige a posição do satelite usando o daly calculado usando as estimativas de posição encontrado
  corrected_measurements_by_epoch.append(corrected)
  pos_solutions.append(raw.calc_pos_fix(corrected)) # calcula a estimativa da posição usando as posições de satélite corrigidas em relação ao delay da transmissão

print("coordenadas no sistema ECEF")
for i,sol in enum(pos_solutions):
    print('epoch: ' + str(1))
    print('x: ' + str(sol[0][0]))
    print('y: ' + str(sol[0][1]))
    print('z: ' + str(sol[0][2]))
    print()
