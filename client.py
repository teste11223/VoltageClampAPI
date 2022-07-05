#!/usr/bin/env python
import json
import requests

url = 'http://localhost:5000/'
head = {'Content-Type': 'application/json'}

if False:
    data = {
        #'membrane_conductance': 10,
        'membrane_capacitance': 20,
        'pipette_capacitance': 5,
        #'series_resistance': 30,
        'esimated_membrane_capacitance': 25,
        'esimated_pipette_capacitance': 4,
        #'esimated_series_resistance': 25,
        #'series_resistance_compensation_enabled': True,
        #'series_resistance_compensation': 70,
        'effective_voltage_offset': 0,
    }

    r = requests.post(f'{url}', data=json.dumps(data), headers=head)
    print(r.json())


r = requests.get(f'{url}')

for k, v in r.json().items():
    print(k)
    for kk, vv in v.items():
        print(f'  {kk}: {vv}')

