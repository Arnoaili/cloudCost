#!/usr/bin/python
# -*- coding: utf-8 -*-

from models import *
from django.db.models import Q
from django.http import JsonResponse
from django.conf import settings
import os, datetime
import xlrd


class ExcelData():
    def __init__(self, file_):
        self.file = file_
        # self.filepath2 = os.path.join(settings.FILES_PATH, 'tengxunyun2.xlsx')
        self.lastmonth = (datetime.date.today().replace(day=1) - datetime.timedelta(1)).strftime('%Y%m')
        # self.month = datetime.date.today().strftime('%Y%m')
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
                                        percentage=data[1],
                                        month=self.lastmonth
                                        )
                except:
                    return 'contenterror'
            return 'success'
        return 'exist'


# def fluxapi(request):
#     month = Flux.objects.last().month
#     fluxset = Flux.objects.filter(month=month)
#     fluxlist = []
#     for flux in fluxset:
#         fluxdict = {}
#         fluxdict['projectName'] = flux.projectName
#         fluxdict['broadbandUsage'] = flux.broadbandUsage
#         fluxdict['percentage'] = flux.percentage
#         fluxdict['region'] = flux.region
#         fluxdict['expense'] = flux.expense
#         fluxdict['month'] = month
#         fluxlist.append(fluxdict)
#     return JsonResponse(fluxlist, safe=False)

# def updateflux(request):
#     if request.method == 'POST':
#         print '##########', request.body, type(request.body)
#         data = request.body.split('&')
#         for dat in data:
#             if not dat:
#                 return JsonResponse('请输入正确的参数！', safe=False)
#         print '@@@@@@@@@@', data[0].decode('utf-8').encode('gbk'), data[-1]
#         projectName = data[0].decode('utf-8')
#         month = data[-1]
#         region = data[3].decode('utf-8')
#         check = Flux.objects.filter(Q(month=month) & Q(projectName=projectName) & Q(region=region))
#         if check:
#             obj = Flux.objects.get(Q(month=month) & Q(projectName=projectName) & Q(region=region))
#             obj.projectName = data[0]
#             obj.broadbandUsage = data[1]
#             obj.percentage = data[2]
#             obj.region = data[3]
#             obj.expense = data[4]
#             obj.month = data[5]
#             obj.save()
#             return JsonResponse('更新成功！', safe=False)
#         else:
#             Flux.objects.create(projectName=data[0],
#                                 broadbandUsage=float(data[1]),
#                                 percentage=data[2],
#                                 region=data[3],
#                                 expense=float(data[4]),
#                                 month=data[5]
#                                 )
#             return JsonResponse('创建成功！', safe=False)
#     return JsonResponse({})

# def platapi(request):
#     month = Plat.objects.last().month
#     platset = Plat.objects.filter(month=month)
#     platlist = []
#     for plat in platset:
#         platdict = {}
#         platdict['projectName'] = plat.projectName
#         platdict['percentage'] = plat.percentage
#         platdict['month'] = month
#         platlist.append(platdict)
#     return JsonResponse(platlist, safe=False)

# def updateplat(request):
#     if request.method == 'POST':
#         print '##########', request.body, type(request.body)
#         data = request.body.split('&')
#         for dat in data:
#             if not dat:
#                 return JsonResponse('请输入正确的参数！', safe=False)
#         projectName = data[0].decode('utf-8')
#         month = data[-1]
#         check = Plat.objects.filter(Q(month=month) & Q(projectName=projectName))
#         if check:
#             obj = Plat.objects.get(Q(month=month) & Q(projectName=projectName))
#             obj.projectName = data[0]
#             obj.percentage = data[1]
#             obj.month = data[2]
#             obj.save()
#             return JsonResponse('更新成功！', safe=False)
#         else:
#             Plat.objects.create(projectName=data[0],
#                                 percentage=data[1],
#                                 month=data[2]
#                                 )
#             return JsonResponse('创建成功！', safe=False)
#     return JsonResponse({})

# def uploadfile(myfile, filetype):
#     if not myfile:
#         dstatus = "Please select the file to upload!"
#     else:
#         path_dst_file = os.path.join(settings.FILES_PATH, myfile.name)
#         destination = open(path_dst_file,'wb+')    # 打开特定的文件进行二进制的写操作
#         for chunk in myfile.chunks():      # 分块写入文件
#             destination.write(chunk)
#         destination.close()
#         dstatus = "%s upload success!"%(myfile.name)
#         excel = ExcelData(path_dst_file)
#         info = excel.open_excel()
#         if info == 'error':
#             return '文件类型错误！'
#         elif info == 'nodata':
#             return '空文件！'
#         if filetype == 'flux':
#             result = excel.import_flux_data_to_db()
#         elif filetype == 'plat':
#             result = excel.import_plat_data_to_db()
#         if result == 'contenterror':
#             return '文件内容错误！'
#         elif result == 'success':
#             return 'Excel数据导入成功！'
#         elif result == 'exist':
#             return '数据已存在！'
#
# def importfluxfile(request):
#     if request.method == 'POST':
#         myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
#         print "^^^^^^^^^^", myfile, type(myfile), myfile.name
#         dstatus = uploadfile(myfile, 'flux')
#         print '**********', dstatus
#         return JsonResponse(dstatus, safe=False)
#     return JsonResponse({})
#
# def importplatfile(request):
#     if request.method == 'POST':
#         myfile =request.FILES.get("file", None)    # 获取上传的文件，如果没有文件，则默认为None
#         print "^^^^^^^^^^", myfile, type(myfile), myfile.name
#         dstatus = uploadfile(myfile, 'plat')
#         return JsonResponse(dstatus, safe=False)
#     return JsonResponse({})

# def deleteflux(request):
#     if request.method == 'POST':
#         print '##########', request.body, type(request.body)
#         data = request.body.split('&')
#         projectName = data[0]
#         region = data[1]
#         month = data[2]
#         Flux.objects.filter(Q(month=month) & Q(projectName=projectName) & Q(region=region)).delete()
#         return JsonResponse('删除成功！', safe=False)
#     return JsonResponse({})

# def deleteplat(request):
#     if request.method == 'POST':
#         print '##########', request.body, type(request.body)
#         data = request.body.split('&')
#         projectName = data[0]
#         month = data[1]
#         Plat.objects.filter(Q(month=month) & Q(projectName=projectName)).delete()
#         return JsonResponse('删除成功！', safe=False)
#     return JsonResponse({})
