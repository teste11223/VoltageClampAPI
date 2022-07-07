#!/usr/bin/env python
#
# Very simple test client, in Python.
#
# The port can be set to 80 by adding command line arg "80".
#
import json
import sys

import requests


port = 80 if '80' in sys.argv else '5000'
url = f'http://127.0.0.1:{port}'
head = {'Content-Type': 'application/json'}

if 'list' in sys.argv:

    # List of simulations
    r = requests.get(f'{url}')
    j = r.json()

    print('Simulations:')
    for s in j['simulations']:
        print(f'  {s}')


elif 'get' in sys.argv:

    # Simulation info
    r = requests.get(f'{url}/default')
    j = r.json()

    print(j['description'])
    for p in j['parameters']:
        print(p['name'])
        for k, v in p.items():
            if k != 'name':
                print(f'  {k}: {v}')

else:

    # Run a simulation
    data = json.dumps({
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
    })

    r = requests.post(f'{url}/default', data=data, headers=head)
    print(r.json())

