#!/usr/bin/env python
#
# Very simple test client, in Python.
#
import json
import sys

import requests


url = 'http://127.0.0.1:5000/default'
head = {'Content-Type': 'application/json'}


if 'get' in sys.argv:

    r = requests.get(f'{url}')
    j = r.json()

    print(j['description'])
    for p in j['parameters']:
        print(p['name'])
        for k, v in p.items():
            if k != 'name':
                print(f'  {k}: {v}')

else:

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

