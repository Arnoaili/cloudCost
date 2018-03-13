#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib, hmac, base64, urllib, urllib2, json
import time, datetime
from django.conf import settings
from models import *
import sys, os
from qcloudsdk.src.QcloudApi.qcloudapi import QcloudApi
import xlrd


# 获取项目账单数据
class projectExpense():
    def __init__(self):
        self.flag = 0
        self.prePay = 0
        self.postPay = 0
        self.returnPay = 0
        self.nextPay = 0
        self.today = datetime.date.today()
        self.secretKey = settings.SECRETKEY
        self.SecretId = settings.SECRETID
        # 查询当月
        self.month = (self.today.replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')

    def get_data(self, module, params):
        # 生成签名
        paraStr = '&'.join(params)
        srcStr = 'GET' + module + '.api.qcloud.com/v2/index.php?' + paraStr
        # print srcStr
        signature = base64.b64encode(hmac.new(self.secretKey, srcStr, digestmod=hashlib.sha256).digest())
        # print signature
        # 生成url
        signatureEncode = urllib.urlencode({'Signature':signature})
        url = 'https://' + module + '.api.qcloud.com/v2/index.php?' + paraStr + '&' + signatureEncode
        print url
        data = json.loads(urllib2.urlopen(url).read())
        totalAmount = data['data']['amount']
        if totalAmount < 0:
            totalAmount = -totalAmount
        dataSet = data['data']['data']
        deductTotal = self.import_data_to_db(dataSet)
        print totalAmount, deductTotal
        if self.flag == 4:
            return deductTotal
        else:
            return totalAmount - deductTotal

    def import_data_to_db(self, dataSet):
        deductTotal = 0
        # 查询上月最后一天
        days = int((self.today.replace(day=1) - datetime.timedelta(1)).strftime('%d'))
        lastMonthDate = (self.today.replace(day=1) - datetime.timedelta(1+days)).strftime('%Y-%m-%d') + ' 23:59:59'
        # 查询当月最后一天
        lastDate = (self.today.replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m-%d') + ' 23:59:59'
        for data in dataSet:
            if self.flag == 2 and data['endTime'] == lastMonthDate:
                deductTotal += -int(data['amount'])
                continue
            if self.flag == 4 and data['endTime'] != lastDate:
                continue
            if self.flag == 4 and data['endTime'] == lastDate:
                deductTotal += -int(data['amount'])
            if self.flag == 3:
                amount = data['returnAmount']
            else:
                amount = data['amount']
            if QcloudDeal.objects.filter(dealId=data['id']):
                continue
            QcloudDeal.objects.create(dealId=data['id'],
                                      payMode=data['payMode'],
                                      payType=data['payType'],
                                      platform=data['platform'],
                                      region=data['region'],
                                      productCode=data['productCode'],
                                      subProductCode=data['subProductCode'],
                                      instanceId=data['instanceId'],
                                      amount=amount,
                                      startTime=data['startTime'],
                                      endTime=data['endTime'],
                                      projectId=data['projectId'],
                                      month=self.month
                                    )
        return deductTotal

    def deliverParameter(self, startMonth, endMonth, payMode, payType):
        # 查询模块
        module = 'feecenter'
        # 查询参数
        Action= 'DescribeResourceBills'
        Timestamp = int(time.time())
        Nonce= 183084054
        # Region= 'ap-guangzhou'
        uin = 2623509340
        SignatureMethod = 'HmacSHA256'
        # 生成参数列表，参数需按ASSIC码排序
        params = [
                    "Action=" + Action,
                    "Nonce=" + str(Nonce),
                    # "Region=" + Region,
                    "SecretId=" + self.SecretId,
                    "SignatureMethod=" + "HmacSHA256",
                    "Timestamp=" + str(Timestamp),
                    "endMonth=" + endMonth,
                    "payMode=" + payMode,
                    "payType=" + payType,
                    "startMonth=" + startMonth,
                    "uin=" + str(uin)
                ]
        totalAmount = self.get_data(module, params)
        print 'Data has been obtained : ', endMonth, '&', payMode, '&', payType
        return totalAmount

    def main(self):
        # 查询下月
        nextMonth = self.today.strftime('%Y-%m')
        # 当月预付费
        startMonth = self.month
        endMonth = self.month
        payMode = 'prePay'
        payType = 'deduct' # 扣费：return    退款：deduct
        self.flag = 1
        self.prePay = self.deliverParameter(startMonth, endMonth, payMode, payType)
        # 当月后付费
        payMode = 'postPay'
        payType = 'deduct'
        self.flag = 2
        self.postPay = self.deliverParameter(startMonth, endMonth, payMode, payType)
        # 当月退款
        payMode = 'prePay'
        payType = 'return'
        self.flag = 3
        self.returnPay = self.deliverParameter(startMonth, endMonth, payMode, payType)
        # 下月后付费
        startMonth = nextMonth
        endMonth = nextMonth
        payMode = 'postPay'
        payType = 'deduct'
        self.flag = 4
        self.nextPay = self.deliverParameter(startMonth, endMonth, payMode, payType)
        # 记录总费用
        if not ExpenseTotal.objects.filter(month=self.month):
            totalExpense = self.prePay+self.postPay+self.nextPay-self.returnPay
            ExpenseTotal.objects.create(month=self.month,
                                        prePayAmount=self.prePay,
                                        postPayAmount=self.postPay,
                                        returnAmount=self.returnPay,
                                        nextPostAmount=self.nextPay,
                                        totalExpense=totalExpense
                                        )

# 获取项目列表
class projects():
    def get_projects(self):
        module = 'account'
        action = 'DescribeProject'
        config = {
            'Region': 'bj',
            'secretId': settings.SECRETID,
            'secretKey': settings.SECRETKEY,
            'method': 'get'
        }
        params = {'allList': 1}
        try:
            service = QcloudApi(module, config)
            print service.generateUrl(action, params)
            data = json.loads(service.call(action, params))
            #service.setRequestMethod('get')
            #print service.call('DescribeCdnEntities', {})
        except Exception, e:
            print 'exception:', e
        return data

    def import_data_to_db(self):
        dataSet = self.get_projects()['data']
        for data in dataSet:
            if Project.objects.filter(projectId=data['projectId']):
                print data['projectName'], ' exist!'
                continue
            Project.objects.create(projectId= data['projectId'],
                                   projectName= data['projectName']
                                )

# 获取cdn数据并计算比例
class cdnExpense():
    def __init__(self):
        self.today = datetime.date.today()
        self.month = (self.today.replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')

    def get_cdn(self, projectId):
        days = int((self.today.replace(day=1) - datetime.timedelta(1)).strftime('%d'))
        self.startDate = (self.today.replace(day=1) - datetime.timedelta(days)).strftime('%Y-%m-%d')
        self.endDate = (self.today.replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m-%d')
        module = 'cdn'
        action = 'DescribeCdnHostInfo'
        config = {
            'Region': 'gz',
            'secretId': settings.SECRETID,
            'secretKey': settings.SECRETKEY,
            'method': 'get'
        }
        params = {'startDate': self.startDate,
                  'endDate': self.endDate,
                  'statType': 'flux',
                  'projects.0': projectId
                  }
        try:
            service = QcloudApi(module, config)
            print service.generateUrl(action, params)
            # sys.exit()
            data = json.loads(service.call(action, params))
            #service.setRequestMethod('get')
            #print service.call('DescribeCdnEntities', {})
        except Exception, e:
            print 'exception:', e
        return data

    def import_data_to_db(self):
        # data = self.get_cdn(1062118)
        # months = list(StatisticMonth.objects.values_list('statisticMonth',flat=True))
        # if self.month in months:
        #     print("Data of %s has get already!" % self.month)
        #     sys.exit()
        if CdnPercentage.objects.filter(month=self.month):
            print 'Cdn data exist!'
            return
        projectSet = Project.objects.all().exclude(projectId='0')

        # projectIds = list(Project.objects.values_list('projectId', flat=True))
        # for projectId in projectIds:

        for pro in projectSet:
            data = self.get_cdn(int(pro.projectId))

            if data['data']['detail_data'] != []:
                for detail in data['data']['detail_data']:
                    Cdn.objects.create(domainName=detail['host_name'],
                                       projectName=pro.projectName,
                                       flux=detail['host_value'],
                                       startTime=data['data']['start_datetime'],
                                       endTime=data['data']['end_datetime']
                                       )
                print pro.projectName,' has been insert into db!'
        self.calculation()
        # StatisticMonth.objects.create(statisticMonth=self.month)

    def calculation(self):
        # month = (self.today.replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')
        startTime = self.month + '-01 00:00:00'
        flux = Cdn.objects.filter(startTime=startTime).values_list('flux',flat=True)
        totalFlux = sum(map(int, list(flux)))
        project = Cdn.objects.filter(startTime=startTime).values_list('projectName',flat=True)
        projects = list(set(project))
        for project in projects:
            flux = Cdn.objects.filter(startTime=startTime).filter(projectName=project).values_list('flux',flat=True)
            projectTotalFlux = sum(map(int, list(flux)))
            CdnPercentage.objects.create(projectName=project,
                                         percentage=round(float(projectTotalFlux)/totalFlux, 8),
                                         month=self.month
                                        )
        print 'percentage calculation done!'

# 手动导入流量,平台数据,腾讯云非固定费用和其他平台的数据
class ExcelData():
    def __init__(self):
        self.filepath1 = os.path.join(settings.FILES_PATH, '201712plat_percentage.xlsx') #'C:/Users/111/Desktop/tengxunyun1.xlsx'
        self.filepath2 = os.path.join(settings.FILES_PATH, '201712tengxunyun_flux.xlsx')
        self.filepath3 = os.path.join(settings.FILES_PATH, '201712message.xlsx')
        self.filepath4 = os.path.join(settings.FILES_PATH, '201712other_plat_cost.xlsx')
        self.filepath5 = os.path.join(settings.FILES_PATH, '201712big_data_percentage.xlsx')
        self.filepath6 = os.path.join(settings.FILES_PATH, '201712aws.xlsx')
        self.month = (datetime.date.today().replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')
    def open_excel(self, file_):
        workbook = xlrd.open_workbook(file_)
        sheet = workbook.sheet_by_index(0)
        rownum = sheet.nrows
        if rownum == 0:
            print "No data in excel!"
            sys.exit()
        return rownum, sheet

    def import_flux_data_to_db(self):
        rownum, sheet = self.open_excel(self.filepath2)
        for row in range(1, rownum):
            data = sheet.row_values(row)
            Flux.objects.create(projectName=data[0],
                                broadbandUsage=float(data[1][:-5]),
                                percentage=data[2],
                                region=data[3],
                                expense=float(data[4][:-2]),
                                month=self.month
                                )

    def import_plat_data_to_db(self):
        rownum, sheet = self.open_excel(self.filepath1)
        for row in range(1, rownum):
            data = sheet.row_values(row)
            Plat.objects.create(projectName=data[0],
                                region=data[1],
                                version=data[2],
                                percentage=data[3],
                                month=self.month
                                )

    def import_other_data_to_db(self):
        rownum, sheet = self.open_excel(self.filepath3)
        for row in range(1, rownum):
            data = sheet.row_values(row)
            OtherCost.objects.create(usage=data[0],
                                projectName=data[1],
                                cost=data[2],
                                month=self.month
                                )

    def import_other_plat_data_to_db(self):
        rownum, sheet = self.open_excel(self.filepath4)
        for row in range(1, rownum):
            data = sheet.row_values(row)
            OtherPlatCost.objects.create(plat=data[0],
                                projectName=data[1],
                                cost=data[2],
                                month=self.month
                                )

    def import_bigdata_data_to_db(self):
        rownum, sheet = self.open_excel(self.filepath5)
        for row in range(1, rownum):
            data = sheet.row_values(row)
            BigData.objects.create(projectName=data[0],
                                region=data[1],
                                version=data[2],
                                percentage=round(data[3], 4),
                                month=self.month
                                )

    def import_aws_data_to_db(self):
        rownum, sheet = self.open_excel(self.filepath6)
        for row in range(1, rownum):
            data = sheet.row_values(row)
            AwsCost.objects.create(projectName=data[0],
                                region=data[1],
                                version=data[2],
                                serviceCost=data[3],
                                supportCost=data[4],
                                month=self.month
                                )

def main():
    month = (datetime.date.today().replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')
    test = projectExpense()
    test.main()
    test = cdnExpense()
    test.import_data_to_db()
    try:
        ExpenseTotal.objects.get(month=month)
    except:
        return {'data':'qcloud资源账单获取失败！'}
    if not CdnPercentage.objects.filter(month=month):
        return u'qcloud cdn数据获取失败！'
    return {'data':'qcloud最新数据获取成功！'}

if __name__ == '__main__':
    test = projects()
    test.import_data_to_db()

    test = ExcelData()
    test.import_flux_data_to_db()

    main()
