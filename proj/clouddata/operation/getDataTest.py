#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib, hmac, base64, urllib, urllib2, json
import time, datetime
from django.conf import settings
from models import *
import sys, os
from qcloudsdk.src.QcloudApi.qcloudapi import QcloudApi
import xlrd

'''
该列子是获取2018-01的数据
'''
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
        self.month = '2018-01'#(self.today.replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')

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
        lastMonthDate = '2017-12-31 23:59:59'#(self.today.replace(day=1) - datetime.timedelta(1+days)).strftime('%Y-%m-%d') + ' 23:59:59'
        # 查询当月最后一天
        lastDate = '2018-01-31 23:59:59'#(self.today.replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m-%d') + ' 23:59:59'
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
        nextMonth = '2017-12'#self.today.strftime('%Y-%m')
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
        # self.today = datetime.date.today()
        self.month = '2018-01'#(self.today.replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')

    def get_cdn(self, projectId):
        # days = int((self.today.replace(day=1) - datetime.timedelta(1)).strftime('%d'))
        startDate = '2018-01-01'#(self.today.replace(day=1) - datetime.timedelta(days)).strftime('%Y-%m-%d')
        endDate ='2018-01-31' #(self.today.replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m-%d')
        module = 'cdn'
        action = 'DescribeCdnHostInfo'
        config = {
            'Region': 'gz',
            'secretId': settings.SECRETID,
            'secretKey': settings.SECRETKEY,
            'method': 'get'
        }
        params = {'startDate': startDate,
                  'endDate': endDate,
                  'statType': 'flux',
                  'projects.0': projectId
                  }
        try:
            service = QcloudApi(module, config)
            print service.generateUrl(action, params)
            data = json.loads(service.call(action, params))
        except Exception, e:
            print 'exception:', e
        return data

    def import_data_to_db(self):
        if CdnPercentage.objects.filter(month=self.month):
            print 'Cdn data exist!'
            return
        projectSet = Project.objects.all().exclude(projectId='0')

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


if __name__ == '__main__':
    test = projects()
    test.import_data_to_db()

    test = projectExpense()
    test.main()
