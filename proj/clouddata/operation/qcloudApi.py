#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from qcloudsdk.src.QcloudApi.qcloudapi import QcloudApi
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response


def common(region, module, action, params=None):
    config = {
        'Region': region,
        'secretId': settings.SECRETID,
        'secretKey': settings.SECRETKEY,
        'method': 'get'
    }
    if not params:
        params = {}
    try:
        service = QcloudApi(module, config)
        Instances = json.loads(service.call(action, params))
    except Exception, e:
        print 'exception:', e
    return Instances

class GetRegion(APIView):
    def get(self, request, *args, **kwargs):
        module = 'cvm'
        region = 'gz'
        action = 'DescribeRegions'
        cdbInstances = common(region, module, action)
        return Response(cdbInstances)

class GetProject(APIView):
    def get(self, request, *args, **kwargs):
        module = 'account'
        region = 'gz'
        action = 'DescribeProject'
        projectInstances = common(region, module, action)
        return Response(projectInstances)

class GetInstances(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        if data.has_key('moduel') and data.has_key('action') and data.has_key('region'):
            instances = common(data['region'], data['moduel'], data['action'])
            return Response(instances)
        else:
            return Response({'status': 500, 'status': 'parameter error!'})


# from django.http import JsonResponse

# def get_region(request):
#     module = 'cvm'
#     region = 'gz'
#     action = 'DescribeRegions'
#     cdbInstances = common(region, module, action)
#     return JsonResponse(cdbInstances, safe=False)
#
# def get_project(request):
#     module = 'account'
#     region = 'gz'
#     action = 'DescribeProject'
#     projectInstances = common(region, module, action)
#     return JsonResponse(projectInstances, safe=False)

# def get_all_instances(request, region, module):
#     print "*******", region, module
#     if request.method == 'POST':
#         post_data = request.body
#         print post_data
#         data_dict = {}
#         for data in post_data.split('&'):
#             data_dict[data.split('=')[0]] = data.split('=')[1]
#         print data_dict
#         if not data_dict.has_key('action'):
#             return JsonResponse({"status": "error", "description": "parameter error"})
#         action = data_dict["action"]
#         Instances = common(region, module, action)
#         return JsonResponse(Instances, safe=False)
#     return JsonResponse({"status": "error", "description": "No data"})
