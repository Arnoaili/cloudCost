#!/usr/bin/python
# -*- coding: utf-8 -*-

from models import *
from django.db.models import Q
from django.conf import settings
import os, datetime
import xlrd
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse


class ExcelData():
    def __init__(self, file_):
        self.file = file_
        self.lastmonth = (datetime.date.today().replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')
        # self.month = datetime.date.today().strftime('%Y-%m')
    def open_excel(self):
        try:
            workbook = xlrd.open_workbook(self.file)
        except:
            return 'error'
        sheet = workbook.sheet_by_index(0)
        rownum = sheet.nrows
        if rownum == 0:
            print "No data in excel!"
            return 'nodata'
        return rownum, sheet

    def import_flux_data_to_db(self):
        rownum, sheet = self.open_excel()
        if not Flux.objects.filter(month=self.lastmonth):
            for row in range(1, rownum):
                data = sheet.row_values(row)
                try:
                    Flux.objects.create(projectName=data[0],
                                        broadbandUsage=float(data[1][:-5]),
                                        percentage=data[2],
                                        region=data[3],
                                        expense=float(data[4][:-2]),
                                        month=self.lastmonth
                                        )
                except:
                    return 'contenterror'
            return 'success'
        return 'exist'

    def import_plat_data_to_db(self):
        rownum, sheet = self.open_excel()
        if not Plat.objects.filter(month=self.lastmonth):
            for row in range(1, rownum):
                data = sheet.row_values(row)
                try:
                    Plat.objects.create(projectName=data[0],
                                        region=data[1],
                                        version=data[2],
                                        percentage=data[3],
                                        month=self.lastmonth
                                        )
                except:
                    return 'contenterror'
            return 'success'
        return 'exist'

    def import_aws_data_to_db(self):
        rownum, sheet = self.open_excel()
        if not AwsCost.objects.filter(month=self.lastmonth):
            for row in range(1, rownum):
                data = sheet.row_values(row)
                try:
                    AwsCost.objects.create(projectName=data[0],
                                        region=data[1],
                                        version=data[2],
                                        serviceCost=data[3],
                                        supportCost=data[4],
                                        month=self.lastmonth
                                        )
                except:
                    return 'contenterror'
            return 'success'
        return 'exist'

    def import_other_plat_data_to_db(self):
        rownum, sheet = self.open_excel()
        if not OtherPlatCost.objects.filter(month=self.lastmonth):
            for row in range(1, rownum):
                data = sheet.row_values(row)
                try:
                    OtherPlatCost.objects.create(plat=data[0],
                                        projectName=data[1],
                                        cost=data[2],
                                        month=self.lastmonth
                                        )
                except:
                    return 'contenterror'
            return 'success'
        return 'exist'

    def import_bigdata_data_to_db(self):
        rownum, sheet = self.open_excel()
        if not BigData.objects.filter(month=self.lastmonth):
            for row in range(1, rownum):
                data = sheet.row_values(row)
                try:
                    BigData.objects.create(projectName=data[0],
                                        region=data[1],
                                        version=data[2],
                                        percentage=round(data[3], 4),
                                        month=self.lastmonth
                                        )
                except:
                    return 'contenterror'
            return 'success'
        return 'exist'

    def import_other_data_to_db(self):
        rownum, sheet = self.open_excel()
        if not OtherCost.objects.filter(month=self.lastmonth):
            for row in range(1, rownum):
                data = sheet.row_values(row)
                try:
                    OtherCost.objects.create(usage=data[0],
                                        projectName=data[1],
                                        cost=data[2],
                                        month=self.lastmonth
                                        )
                except:
                    return 'contenterror'
            return 'success'
        return 'exist'

def uploadfile(myfile, filetype):
    if not myfile:
        dstatus = "Please select the file to upload!"
    else:
        path_dst_file = os.path.join(settings.FILES_PATH, myfile.name)
        destination = open(path_dst_file,'wb+')    # 打开特定的文件进行二进制的写操作
        for chunk in myfile.chunks():      # 分块写入文件
            destination.write(chunk)
        destination.close()
        dstatus = "%s upload success!"%(myfile.name)
        excel = ExcelData(path_dst_file)
        info = excel.open_excel()
        if info == 'error':
            return '文件类型错误！'
        elif info == 'nodata':
            return '空文件！'
        if filetype == 'flux':
            result = excel.import_flux_data_to_db()
        elif filetype == 'plat':
            result = excel.import_plat_data_to_db()
        elif filetype == 'aws':
            result = excel.import_aws_data_to_db()
        elif filetype == 'otherplat':
            result = excel.import_other_plat_data_to_db()
        elif filetype == 'bigdata':
            result = excel.import_bigdata_data_to_db()
        elif filetype == 'qcloudothercost':
            result = excel.import_other_data_to_db()
        if result == 'contenterror':
            return '文件内容错误！'
        elif result == 'success':
            return 'Excel数据导入成功！'
        elif result == 'exist':
            return '数据已存在！'

def UploadFluxFile(request):
    if request.method == 'POST':
        myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
        dstatus = uploadfile(myfile, 'flux')
        return JsonResponse({'data':dstatus})

# class UploadFluxFile(APIView):
#     def post(self, request, *args, **kwargs):
#         myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
#         print "****", myfile, type(myfile), myfile.name
#         dstatus = uploadfile(myfile, 'flux')
#         return Response({'data':dstatus})

def UploadPlatFile(request):
    if request.method == 'POST':
        myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
        dstatus = uploadfile(myfile, 'plat')
        return JsonResponse({'data':dstatus})

# class UploadPlatFile(APIView):
#     def post(self, request, *args, **kwargs):
#         myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
#         print "****", myfile, type(myfile), myfile.name
#         dstatus = uploadfile(myfile, 'plat')
#         return Response({'data':dstatus})

def UploadAwsFile(request):
    if request.method == 'POST':
        myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
        dstatus = uploadfile(myfile, 'aws')
        return JsonResponse({'data':dstatus})

# class UploadAwsFile(APIView):
#     def post(self, request, *args, **kwargs):
#         myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
#         dstatus = uploadfile(myfile, 'aws')
#         return Response({'data':dstatus})

def UploadOtherPlatFile(request):
    if request.method == 'POST':
        myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
        dstatus = uploadfile(myfile, 'otherplat')
        return JsonResponse({'data':dstatus})

# class UploadOtherPlatFile(APIView):
#     def post(self, request, *args, **kwargs):
#         myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
#         dstatus = uploadfile(myfile, 'otherplat')
#         return Response({'data':dstatus})

def UploadBigDataFile(request):
    if request.method == 'POST':
        myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
        dstatus = uploadfile(myfile, 'bigdata')
        return JsonResponse({'data':dstatus})

# class UploadBigDataFile(APIView):
#     def post(self, request, *args, **kwargs):
#         myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
#         dstatus = uploadfile(myfile, 'bigdata')
#         return Response({'data':dstatus})

def UploadQcloudOtherCostFile(request):
    if request.method == 'POST':
        myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
        dstatus = uploadfile(myfile, 'qcloudothercost')
        return JsonResponse({'data':dstatus})

# class UploadQcloudOtherCostFile(APIView):
#     def post(self, request, *args, **kwargs):
#         myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
#         dstatus = uploadfile(myfile, 'qcloudothercost')
#         return Response({'data':dstatus})
