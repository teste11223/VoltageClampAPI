#!/usr/bin/env python
import json
from requests import post

url = 'http://localhost:5000/'
head = {'Content-Type': 'application/json'}
data = {'one': 2}

r = post(f'{url}', data=json.dumps(data), headers=head)
print(r.json())
