# -*- coding: utf-8 -*-


import requests


r = requests.get('http://127.0.0.1:8000/q/v1/project/')
print r.json()

data = {'region':'bj', 'moduel':'cdb', 'action':'DescribeCdbInstances'}
r = requests.post('http://127.0.0.1:8000/q/v1/instances/', data=data)

print r.text
print type(r.text)


# get ### curl http://127.0.0.1:8000/q/v1/project/
# post ### curl http://127.0.0.1:8000/q/v1/instances/ -d "region=bj&moduel=cdb&action=DescribeCdbInstances" -X POST