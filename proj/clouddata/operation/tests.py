# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

# Create your tests here.
# 通过封装的腾讯云SDK获取数据的例子

import urllib
import urllib2
import json

def get_qcloud_region():
    region_url = 'http://192.168.80.20:2000/q/v1/region/'
    req = urllib2.Request(region_url)
    response = urllib2.urlopen(req)
    regionSet = json.loads(response.read())['regionSet']
    regionCode = []
    for region in regionSet:
        regionCode.append(region['regionCode'])
    return regionCode

def get_db_instance():
    db_style = {"cdb": "DescribeCdbInstances", "redis": "DescribeRedis"}
    for db in db_style.keys():
        for regionCode in ['bj', 'gz', 'sh', 'cd']:
            url = '/'.join(['http://192.168.80.20:2000/q/v1', regionCode, db+'/'])
            print url
            headers = { 'User-Agent' : 'Mozilla/4.0' }
            values = {'action': db_style[db], 'params':{}}
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data, headers)
            response = json.loads(urllib2.urlopen(req).read())
            if db == 'cdb':
                instancesList = response['cdbInstanceSet']
            elif db == "redis":
                instancesList = response['data']['redisSet']
            print instancesList

def get_cvm():
	url = 'http://192.168.80.20:2000/q/v1/gz/cvm/'
	user_agent = 'Mozilla/4.0'
	values = {'action':'DescribeInstances', 'params':{}}
	headers = { 'User-Agent' : user_agent }
	data = urllib.urlencode(values)
	req = urllib2.Request(url, data, headers)
	response = urllib2.urlopen(req)
	print response.read()

get_cvm()

#get_db_instance()


# url = 'http://192.168.80.20:2000/q/v1/bj/cdb/'
# #user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
# user_agent = 'Mozilla/4.0'
# # values = {'region':'gz', 'module':'cdb', 'action':'DescribeCdbInstances', 'params':{}}
# values = {'action':'DescribeCdbInstances', 'params':{}}
# headers = { 'User-Agent' : user_agent }
# data = urllib.urlencode(values)
# req = urllib2.Request(url, data, headers)
# response = urllib2.urlopen(req)
# print response.read()
