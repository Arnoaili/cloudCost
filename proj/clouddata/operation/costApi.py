#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import datetime
from models import *
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from cost import GetCost, exportExcel
from getQcloudData import main
from serializer import *
from django.http import JsonResponse

currentMonth = (datetime.date.today().replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')


class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        series1 = []
        months = list(ChinaPerMonthCost.objects.distinct().values_list("month", flat=True))
        projects = list(ChinaPerMonthCost.objects.distinct().values_list("projectName", flat=True))
        for pro in projects:
            if pro not in ('大数据','平台支撑','公司公共'):
                cost = []
                for month in months:
                    try:
                        total = ChinaPerMonthCost.objects.get(Q(projectName=pro) & Q(month=month)).total
                        cost.append(total)
                    except:
                        cost.append(0)
                ser = {}
                ser['name'] = pro
                ser['data'] = cost
                series1.append(ser)
        series2 = []
        projects_ = list(OverseasPerMonthCost.objects.distinct().values_list("projectName", "version"))
        for pro in projects_:
            if pro[0] not in ('平台支撑','公司公共'):
                cost = []
                for month in months:
                    try:
                        total = OverseasPerMonthCost.objects.get(Q(projectName=pro[0]) &Q(version=pro[1])& Q(month=month)).total
                        cost.append(total)
                    except:
                        cost.append(0)
                ser = {}
                ser['name'] = pro[0]+'('+pro[1]+')'
                ser['data'] = cost
                series2.append(ser)
        data = {}
        data['xAxis'] = months
        data['series1'] = series1
        data['series2'] = series2
        return Response(data)

def CostView(request):
    def common(month):
        chinadataset = ChinaPerMonthCost.objects.filter(month=month)
        overseasdataset = OverseasPerMonthCost.objects.filter(month=month)
        qcloudset = QcloudCost.objects.filter(month=month)
        aliset = AliCost.objects.filter(month=month)
        zhaoweiset = ZhaoWeiCost.objects.filter(month=month)
        luguset = LuGuCost.objects.filter(month=month)
        ucloudset = UcloudCost.objects.filter(month=month)
        awsset = AwsShareCost.objects.filter(month=month)
        if chinadataset:
            chinaser = ChinaPerMonthCostSerializer(instance=chinadataset, many=True)
            overseasser = OverseasPerMonthCostSerializer(instance=overseasdataset, many=True)
            qcloudser = QcloudCostSerializer(instance=qcloudset, many=True)
            aliser = AliCostSerializer(instance=aliset, many=True)
            zhaoweiser = ZhaoWeiCostSerializer(instance=zhaoweiset, many=True)
            luguser = LuGuCostSerializer(instance=luguset, many=True)
            ucloudser = UcloudCostSerializer(instance=ucloudset, many=True)
            awsser = AwsCostSerializer(instance=awsset, many=True)
            data = {'chinaCostApi':chinaser.data, 'awsCostApi':overseasser.data}
            exportExcel(chinaser.data, overseasser.data, qcloudser.data,aliser.data,\
                        zhaoweiser.data,luguser.data,ucloudser.data,awsser.data,month)
            return data
        else:
            return {'data': 'noData'}
    if request.method == 'GET':
        month = (datetime.date.today().replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')
        res = common(month)
        global currentMonth
        currentMonth = month
        return JsonResponse(res)
    elif request.method == 'POST':
        data = re.search('.*([0-9]{4})-([0-9]{2})$', request.body)
        if not data:
            return Response({'data': 'timeError'})
        month = data.group(1) + '-' +data.group(2)
        global currentMonth
        currentMonth = month
        res = common(month)
        return JsonResponse(res)
    
#  由于使用登录认证后，restful view 发起post请求会被forbidden，产生403 错误，目前没有解决方案，所以使用原始view方法
# class CostView(APIView):
#     def common(self, month):
#         chinadataset = ChinaPerMonthCost.objects.filter(month=month)
#         overseasdataset = OverseasPerMonthCost.objects.filter(month=month)
#         qcloudset = QcloudCost.objects.filter(month=month)
#         aliset = AliCost.objects.filter(month=month)
#         zhaoweiset = ZhaoWeiCost.objects.filter(month=month)
#         luguset = LuGuCost.objects.filter(month=month)
#         ucloudset = UcloudCost.objects.filter(month=month)
#         awsset = AwsShareCost.objects.filter(month=month)
#         if chinadataset:
#             chinaser = ChinaPerMonthCostSerializer(instance=chinadataset, many=True)
#             overseasser = OverseasPerMonthCostSerializer(instance=overseasdataset, many=True)
#             qcloudser = QcloudCostSerializer(instance=qcloudset, many=True)
#             aliser = AliCostSerializer(instance=aliset, many=True)
#             zhaoweiser = ZhaoWeiCostSerializer(instance=zhaoweiset, many=True)
#             luguser = LuGuCostSerializer(instance=luguset, many=True)
#             ucloudser = UcloudCostSerializer(instance=ucloudset, many=True)
#             awsser = AwsCostSerializer(instance=awsset, many=True)
#             data = {'chinaCostApi':chinaser.data, 'awsCostApi':overseasser.data}
#             exportExcel(chinaser.data, overseasser.data, qcloudser.data,aliser.data,\
#                         zhaoweiser.data,luguser.data,ucloudser.data,awsser.data,month)
#             return data
#         else:
#             return {'data': 'noData'}
#     def get(self, request, *args, **kwargs):
#         month = (datetime.date.today().replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')
#         res = self.common(month)
#         global currentMonth
#         currentMonth = month
#         return Response(res)
#     def post(self, request, *args, **kwargs):
#         data = re.search('.*([0-9]{4})-([0-9]{2})$', request.body)
#         if not data:
#             return Response({'data': 'timeError'})
#         month = data.group(1) + '-' +data.group(2)
#         global currentMonth
#         currentMonth = month
#         res = self.common(month)
#         return Response(res)

def GetExcel(request):
    if request.method == 'POST':
        return JsonResponse({'data': currentMonth})

# class GetExcel(APIView):
#     def post(self, request, *args, **kwargs):
#         return Response({'data': currentMonth})

def SyncQcloud(request):
    if request.method == 'POST':
        result = main()
        return JsonResponse(result)

# class SyncQcloud(APIView):
#     def post(self, request, *args, **kwargs):
#         result = main()
#         return Response(result)

def Calculate(request):
    if request.method == 'POST':
        month = currentMonth
        cost = GetCost(month)
        result = cost.save_cost_to_db()
        return JsonResponse(result)

# class Calculate(APIView):
#     def post(self, request, *args, **kwargs):
#         month = currentMonth
#         cost = GetCost(month)
#         result = cost.save_cost_to_db()
#         return Response(result)

class sample(object):
    def __init__(self, tableName, serializer_):
        self.tableName = tableName
        self.serializer_ = serializer_
    def get(self):
        month = self.tableName.objects.last().month
        dataset = self.tableName.objects.filter(month=month)
        ser = self.serializer_(instance=dataset, many=True)
        return ser
    def post(self, data, obj):
        if obj:
            ser = self.serializer_(obj, data=data)
        else:
            ser = self.serializer_(data=data)
        if ser.is_valid():
            ser.save()
            return {'status':200, 'data':'success!'}
        else:
            return {'status':500, 'data':'fail!'}

def FluxCostView(request):
    module = sample(Flux, FluxSerializer)
    if request.method == 'GET':
        ser = module.get()
        return JsonResponse(ser.data, safe=False)
    elif request.method == 'POST':
        projectName = request.POST['projectName']
        month = request.POST['month']
        region = request.POST['region']
        broadbandUsage = request.POST['broadbandUsage']
        percentage = request.POST['percentage']
        expense = request.POST['expense']
        data = {'projectName':projectName,'broadbandUsage':broadbandUsage,'percentage':percentage,'region':region,'expense':expense,'month':month}
        check = Flux.objects.filter(Q(month=month) & Q(projectName=projectName) & Q(region=region))
        if check:
            obj = Flux.objects.get(Q(month=month) & Q(projectName=projectName) & Q(region=region))
        else:
            obj = None
        ser = module.post(data, obj)
        return JsonResponse(ser)
    elif request.method == 'DELETE':
        data = request.body.split('&')
        projectName = data[0]
        region = data[1]
        month = data[2]
        Flux.objects.get(Q(month=month) & Q(projectName=projectName) & Q(region=region)).delete()
        return JsonResponse({'status':200, 'data':'success!'})

# class FluxCostView(sample, APIView):
#     def __init__(self):
#         super(FluxCostView,self).__init__(Flux, FluxSerializer)
#     def get(self, request, *args, **kwargs):
#         # month = Flux.objects.last().month
#         # fluxset = Flux.objects.filter(month=month)
#         # ser = FluxSerializer(instance=fluxset, many=True)
#         ser = super(FluxCostView,self).get()
#         return Response(ser.data)
#     def post(self, request, *args, **kwargs):
#         print '********', request.data
#         data = request.data
#         projectName = data['projectName']
#         month = data['month']
#         region = data['region']
#         check = Flux.objects.filter(Q(month=month) & Q(projectName=projectName) & Q(region=region))
#         # if check:
#         #     obj = Flux.objects.get(Q(month=month) & Q(projectName=projectName) & Q(region=region))
#         #     serializer = FluxSerializer(obj, data=new)
#         # else:
#         #     serializer = FluxSerializer(data=new)
#         # if serializer.is_valid():
#         #     serializer.save()
#         #     return Response({'status':200, 'data':'success!'})
#         # else:
#         #     return Response({'status':500, 'data':'fail!'})
#         if check:
#             obj = Flux.objects.get(Q(month=month) & Q(projectName=projectName) & Q(region=region))
#         else:
#             obj = None
#         ser = super(FluxCostView,self).post(data, obj)
#         return Response(ser)
#
#     def delete(self, request, *args, **kwargs):
#         data = request.data
#         projectName = data['projectName']
#         region = data['region']
#         month = data['month']
#         Flux.objects.get(Q(month=month) & Q(projectName=projectName) & Q(region=region)).delete()
#         return Response({'status':200, 'data':'success!'})

def PlatPercentageView(request):
    module = sample(Plat, PlatSerializer)
    if request.method == 'GET':
        ser = module.get()
        return JsonResponse(ser.data, safe=False)
    elif request.method == 'POST':
        projectName = request.POST['projectName']
        month = request.POST['month']
        region = request.POST['region']
        percentage = request.POST['percentage']
        version = request.POST['version']
        data = {'projectName':projectName, 'region':region, 'version':version, 'percentage':percentage, 'month':month}
        check = Plat.objects.filter(Q(month=month) & Q(projectName=projectName) & Q(version=version))
        if check:
            obj = Plat.objects.get(Q(month=month) & Q(projectName=projectName) & Q(version=version))
        else:
            obj = None
        ser = module.post(data, obj)
        return JsonResponse(ser)
    elif request.method == 'DELETE':
        data = request.body.split('&')
        projectName = data[0]
        version = data[1]
        month = data[2]
        Plat.objects.get(Q(month=month) & Q(projectName=projectName) & Q(version=version)).delete()
        return JsonResponse({'status':200, 'data':'success!'})

# class PlatPercentageView(sample, APIView):
#     def __init__(self):
#         super(PlatPercentageView,self).__init__(Plat, PlatSerializer)
#     def get(self, request, *args, **kwargs):
#         ser = super(PlatPercentageView,self).get()
#         return Response(ser.data)
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         check = Plat.objects.filter(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(version=data['version']))
#         if check:
#             obj = Plat.objects.get(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(version=data['version']))
#         else:
#             obj = None
#         ser = super(PlatPercentageView,self).post(data, obj)
#         return Response(ser)
#     def delete(self, request, *args, **kwargs):
#         data = request.data
#         Plat.objects.get(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(version=data['version'])).delete()
#         return Response({'status':200, 'data':'success!'})

def AwsCostView(request):
    module = sample(AwsCost, AwsSerializer)
    if request.method == 'GET':
        ser = module.get()
        return JsonResponse(ser.data, safe=False)
    elif request.method == 'POST':
        projectName = request.POST['projectName']
        month = request.POST['month']
        region = request.POST['region']
        serviceCost = request.POST['serviceCost']
        supportCost = request.POST['supportCost']
        version = request.POST['version']
        data = {'projectName':projectName, 'region':region, 'version':version, 'serviceCost':serviceCost, 'supportCost':supportCost,'month':month}
        check = AwsCost.objects.filter(Q(month=month) & Q(projectName=projectName) & Q(version=version))
        if check:
            obj = AwsCost.objects.get(Q(month=month) & Q(projectName=projectName) & Q(version=version))
        else:
            obj = None
        ser = module.post(data, obj)
        return JsonResponse(ser)
    elif request.method == 'DELETE':
        data = request.body.split('&')
        projectName = data[0]
        version = data[1]
        month = data[2]
        AwsCost.objects.get(Q(month=month) & Q(projectName=projectName) & Q(version=version)).delete()
        return JsonResponse({'status':200, 'data':'success!'})

# class AwsCostView(sample, APIView):
#     def __init__(self):
#         super(AwsCostView,self).__init__(AwsCost, AwsSerializer)
#     def get(self, request, *args, **kwargs):
#         ser = super(AwsCostView,self).get()
#         return Response(ser.data)
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         check = AwsCost.objects.filter(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(version=data['version']))
#         if check:
#             obj = AwsCost.objects.get(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(version=data['version']))
#         else:
#             obj = None
#         ser = super(AwsCostView,self).post(data, obj)
#         return Response(ser)
#     def delete(self, request, *args, **kwargs):
#         data = request.data
#         AwsCost.objects.get(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(version=data['version'])).delete()
#         return Response({'status':200, 'data':'success!'})

def OtherPlatCostView(request):
    module = sample(OtherPlatCost, OtherPlatCostSerializer)
    if request.method == 'GET':
        ser = module.get()
        return JsonResponse(ser.data, safe=False)
    elif request.method == 'POST':
        projectName = request.POST['projectName']
        month = request.POST['month']
        plat = request.POST['plat']
        cost = request.POST['cost']
        data = {'projectName':projectName, 'plat':plat, 'cost':cost,'month':month}
        check = OtherPlatCost.objects.filter(Q(month=month) & Q(projectName=projectName) & Q(plat=plat))
        if check:
            obj = OtherPlatCost.objects.get(Q(month=month) & Q(projectName=projectName) & Q(plat=plat))
        else:
            obj = None
        ser = module.post(data, obj)
        return JsonResponse(ser)
    elif request.method == 'DELETE':
        data = request.body.split('&')
        projectName = data[0]
        plat = data[1]
        month = data[2]
        OtherPlatCost.objects.get(Q(month=month) & Q(projectName=projectName) & Q(plat=plat)).delete()
        return JsonResponse({'status':200, 'data':'success!'})

# class OtherPlatCostView(sample, APIView):
#     def __init__(self):
#         super(OtherPlatCostView,self).__init__(OtherPlatCost, OtherPlatCostSerializer)
#     def get(self, request, *args, **kwargs):
#         ser = super(OtherPlatCostView,self).get()
#         return Response(ser.data)
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         check = OtherPlatCost.objects.filter(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(plat=data['plat']))
#         if check:
#             obj = OtherPlatCost.objects.get(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(plat=data['plat']))
#         else:
#             obj = None
#         ser = super(OtherPlatCostView,self).post(data, obj)
#         return Response(ser)
#     def delete(self, request, *args, **kwargs):
#         data = request.data
#         OtherPlatCost.objects.get(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(plat=data['plat'])).delete()
#         return Response({'status':200, 'data':'success!'})

def BigDataPercentageView(request):
    module = sample(BigData, BigDataSerializer)
    if request.method == 'GET':
        ser = module.get()
        return JsonResponse(ser.data, safe=False)
    elif request.method == 'POST':
        projectName = request.POST['projectName']
        month = request.POST['month']
        region = request.POST['region']
        version = request.POST['version']
        percentage = request.POST['percentage']
        data = {'projectName':projectName, 'region':region, 'version':version, 'percentage':percentage, 'month':month}
        check = BigData.objects.filter(Q(month=month) & Q(projectName=projectName) & Q(version=version))
        if check:
            obj = BigData.objects.get(Q(month=month) & Q(projectName=projectName) & Q(version=version))
        else:
            obj = None
        ser = module.post(data, obj)
        return JsonResponse(ser)
    elif request.method == 'DELETE':
        data = request.body.split('&')
        projectName = data[0]
        version = data[1]
        month = data[2]
        BigData.objects.get(Q(month=month) & Q(projectName=projectName) & Q(version=version)).delete()
        return JsonResponse({'status':200, 'data':'success!'})


# class BigDataPercentageView(sample, APIView):
#     def __init__(self):
#         super(BigDataPercentageView,self).__init__(BigData, BigDataSerializer)
#     def get(self, request, *args, **kwargs):
#         ser = super(BigDataPercentageView,self).get()
#         return Response(ser.data)
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         check = BigData.objects.filter(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(version=data['version']))
#         if check:
#             obj = BigData.objects.get(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(version=data['version']))
#         else:
#             obj = None
#         ser = super(BigDataPercentageView,self).post(data, obj)
#         return Response(ser)
#     def delete(self, request, *args, **kwargs):
#         data = request.data
#         BigData.objects.get(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(version=data['version'])).delete()
#         return Response({'status':200, 'data':'success!'})

def QcloudOtherCostView(request):
    module = sample(OtherCost, QcloudOtherCostSerializer)
    if request.method == 'GET':
        ser = module.get()
        return JsonResponse(ser.data, safe=False)
    elif request.method == 'POST':
        projectName = request.POST['projectName']
        month = request.POST['month']
        usage = request.POST['usage']
        cost = request.POST['cost']
        data = {'projectName':projectName, 'usage':usage, 'cost':cost,'month':month}
        check = OtherCost.objects.filter(Q(month=month) & Q(projectName=projectName) & Q(usage=usage))
        if check:
            obj = OtherCost.objects.get(Q(month=month) & Q(projectName=projectName) & Q(usage=usage))
        else:
            obj = None
        ser = module.post(data, obj)
        return JsonResponse(ser)
    elif request.method == 'DELETE':
        data = request.body.split('&')
        projectName = data[0]
        usage = data[1]
        month = data[2]
        OtherCost.objects.get(Q(month=month) & Q(projectName=projectName) & Q(usage=usage)).delete()
        return JsonResponse({'status':200, 'data':'success!'})

# class QcloudOtherCostView(sample, APIView):
#     def __init__(self):
#         super(QcloudOtherCostView,self).__init__(OtherCost, QcloudOtherCostSerializer)
#     def get(self, request, *args, **kwargs):
#         ser = super(QcloudOtherCostView,self).get()
#         return Response(ser.data)
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         check = OtherCost.objects.filter(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(usage=data['usage']))
#         if check:
#             obj = OtherCost.objects.get(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(usage=data['usage']))
#         else:
#             obj = None
#         ser = super(QcloudOtherCostView,self).post(data, obj)
#         return Response(ser)
#     def delete(self, request, *args, **kwargs):
#         data = request.data
#         OtherCost.objects.get(Q(month=data['month']) & Q(projectName=data['projectName']) & Q(usage=data['usage'])).delete()
#         return Response({'status':200, 'data':'success!'})
