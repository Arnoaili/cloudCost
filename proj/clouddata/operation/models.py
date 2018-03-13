# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class QcloudDeal(models.Model):
    dealId = models.CharField(u'订单ID', primary_key=True, max_length=20)
    payMode = models.CharField(u'支付模式', max_length=20)
    payType = models.CharField(u'支付类型', max_length=20)
    platform = models.CharField(u'平台', max_length=20)
    region = models.CharField(u'区域', max_length=10)
    productCode = models.CharField(u'产品编码', max_length=50)
    subProductCode = models.CharField(u'子产品编码', max_length=50)
    instanceId = models.CharField(u'实例ID', max_length=50)
    amount = models.FloatField(u'扣费金额/分')
    startTime = models.CharField(u'计费开始时间', max_length=30)
    endTime = models.CharField(u'计费结束时间', max_length=30)
    projectId = models.CharField(u'项目ID', max_length=10)
    month = models.CharField(u'查询月份', max_length=30)

    def __unicode__(self):
        return self.dealId

class ExpenseTotal(models.Model):
    month = models.CharField(u'查询月份', max_length=30)
    prePayAmount = models.FloatField(u'当月预付费/分')
    postPayAmount = models.FloatField(u'当月后付费/分')
    returnAmount = models.FloatField(u'当月退款/分')
    nextPostAmount = models.FloatField(u'下月后付费/分')
    totalExpense = models.FloatField(u'合计/分')

    def __unicode__(self):
        return self.month


class Flux(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    broadbandUsage = models.FloatField(u'带宽使用量')
    percentage = models.FloatField(u'比例') #, max_digits=10, decimal_places=2
    region = models.CharField(u'地域', max_length=10)
    expense = models.FloatField(u'费用/元') #, max_digits=10, decimal_places=2
    month = models.CharField(u'月份', max_length=10)

    def __unicode__(self):
        return self.projectName

class Plat(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    region = models.CharField(u'区域', max_length=10)
    version = models.CharField(u'版本', max_length=10)
    percentage = models.FloatField(u'比例')# , max_digits=10, decimal_places=2
    month = models.CharField(u'月份', max_length=10)

    def __unicode__(self):
        return self.projectName

class Cdn(models.Model):
    domainName = models.CharField(u'域名', max_length=100)
    projectName = models.CharField(u'项目名', max_length=30)
    flux = models.CharField(u'流量', max_length=30)
    startTime = models.CharField(u'开始时间', max_length=50)
    endTime = models.CharField(u'结束时间', max_length=50)

    def __unicode__(self):
        return self.domainName

class CdnPercentage(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    percentage = models.FloatField(u'比例')#, max_digits=10, decimal_places=8
    month = models.CharField(u'月份', max_length=10)

    def __unicode__(self):
        return self.projectName

class Project(models.Model):
    projectId = models.CharField(u'项目ID', primary_key=True, max_length=10)
    projectName = models.CharField(u'项目名', max_length=30)

    def __unicode__(self):
        return self.projectId

class OtherCost(models.Model):
    usage = models.CharField(u'用途', max_length=30)
    projectName = models.CharField(u'项目名', max_length=30)
    cost = models.FloatField(u'费用/元')
    month = models.CharField(u'月份', max_length=10)

class OtherPlatCost(models.Model):
    plat = models.CharField(u'平台', max_length=30)
    projectName = models.CharField(u'项目名', max_length=30)
    cost = models.FloatField(u'费用/元')
    month = models.CharField(u'月份', max_length=10)

class BigData(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    region = models.CharField(u'区域', max_length=10)
    version = models.CharField(u'版本', max_length=10)
    percentage = models.FloatField(u'比例')# , max_digits=10, decimal_places=2
    month = models.CharField(u'月份', max_length=10)

class AwsCost(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    region = models.CharField(u'区域', max_length=10)
    version = models.CharField(u'版本', max_length=10)
    serviceCost = models.FloatField(u'费用/元')
    supportCost = models.FloatField(u'费用/元')
    month = models.CharField(u'月份', max_length=10)

class ChinaPerMonthCost(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    region = models.CharField(u'区域', max_length=10)
    version = models.CharField(u'版本', max_length=10)
    qcloud = models.FloatField(u'qcloud费用/元')
    ali = models.FloatField(u'阿里云费用/元')
    zhaowei = models.FloatField(u'兆维/元')
    lugu = models.FloatField(u'鲁谷/元')
    ucloud = models.FloatField(u'ucloud费用/元')
    common = models.FloatField(u'公司公共分摊/元')
    plat = models.FloatField(u'平台分摊/元')
    bigData = models.FloatField(u'大数据分摊/元')
    total = models.FloatField(u'项目费用合计/元')
    month = models.CharField(u'月份', max_length=10)

class OverseasPerMonthCost(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    region = models.CharField(u'区域', max_length=10)
    version = models.CharField(u'版本', max_length=10)
    service = models.FloatField(u'服务费用/美元')
    support = models.FloatField(u'支持费用/美元')
    common = models.FloatField(u'公司公共分摊/美元')
    plat = models.FloatField(u'平台分摊/美元')
    bigData = models.FloatField(u'大数据分摊/美元')
    total = models.FloatField(u'项目费用合计/美元')
    month = models.CharField(u'月份', max_length=10)

class QcloudCost(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    region = models.CharField(u'区域', max_length=10)
    version = models.CharField(u'版本', max_length=10)
    qcloud = models.FloatField(u'qcloud费用/元')
    common = models.FloatField(u'公司公共分摊/元')
    plat = models.FloatField(u'平台分摊/元')
    total = models.FloatField(u'项目费用合计/元')
    month = models.CharField(u'月份', max_length=10)

class AliCost(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    region = models.CharField(u'区域', max_length=10)
    version = models.CharField(u'版本', max_length=10)
    ali = models.FloatField(u'阿里云费用/元')
    common = models.FloatField(u'公司公共分摊/元')
    plat = models.FloatField(u'平台分摊/元')
    total = models.FloatField(u'项目费用合计/元')
    month = models.CharField(u'月份', max_length=10)

class ZhaoWeiCost(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    region = models.CharField(u'区域', max_length=10)
    version = models.CharField(u'版本', max_length=10)
    zhaowei = models.FloatField(u'兆维/元')
    common = models.FloatField(u'公司公共分摊/元')
    plat = models.FloatField(u'平台分摊/元')
    bigData = models.FloatField(u'大数据分摊/元')
    total = models.FloatField(u'项目费用合计/元')
    month = models.CharField(u'月份', max_length=10)

class LuGuCost(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    region = models.CharField(u'区域', max_length=10)
    version = models.CharField(u'版本', max_length=10)
    lugu = models.FloatField(u'鲁谷/元')
    common = models.FloatField(u'公司公共分摊/元')
    plat = models.FloatField(u'平台分摊/元')
    total = models.FloatField(u'项目费用合计/元')
    month = models.CharField(u'月份', max_length=10)

class AwsShareCost(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    region = models.CharField(u'区域', max_length=10)
    version = models.CharField(u'版本', max_length=10)
    service = models.FloatField(u'服务费用/美元')
    support = models.FloatField(u'支持费用/美元')
    common = models.FloatField(u'公司公共分摊/美元')
    plat = models.FloatField(u'平台分摊/美元')
    bigData = models.FloatField(u'大数据分摊/美元')
    total = models.FloatField(u'项目费用合计/美元')
    month = models.CharField(u'月份', max_length=10)

class UcloudCost(models.Model):
    projectName = models.CharField(u'项目名', max_length=30)
    region = models.CharField(u'区域', max_length=10)
    version = models.CharField(u'版本', max_length=10)
    ucloud = models.FloatField(u'ucloud费用/元')
    common = models.FloatField(u'公司公共分摊/元')
    plat = models.FloatField(u'平台分摊/元')
    total = models.FloatField(u'项目费用合计/元')
    month = models.CharField(u'月份', max_length=10)
