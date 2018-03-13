#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from src.QcloudApi.qcloudapi import QcloudApi

module = 'cdn'
action = 'DescribeCdnHosts'
config = {
    'Region': 'gz',
    'secretId': 'AKIDnX6UjeBdjiXDh4TM9oIbigT6YoyzwtdM',
    'secretKey': 'mNm03vdBXihVDj4DC0c4LXYP4XvBHCyc',
    'method': 'get'
}
params = {}
# params = {
#     'entityFileName': '/test.txt',
#     'entityFile': '/tmp/test.txt',
#     'SignatureMethod':'HmacSHA256',#指定所要用的签名算法，可选HmacSHA256或HmacSHA1，默认为HmacSHA1
# }
try:
    service = QcloudApi(module, config)
    print service.generateUrl(action, params)
    print json.loads(service.call(action, params))
    #service.setRequestMethod('get')
    #print service.call('DescribeCdnEntities', {})
except Exception, e:
    print 'exception:', e
