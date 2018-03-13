#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from models import *
from django.db.models import Q
import datetime
import xlwt
from django.conf import settings
import os
from style import *


class GetCost():
    def __init__(self, month):
        self.month = month
    def qcloud_project_cost(self):
        print u'*********项目费用合计= 资源账单+流量+cdn+其他费用***********'
        otherSet = OtherCost.objects.filter(month=self.month)
        otherTotal = 0
        otherCost = {}
        for other in otherSet:
            if otherCost.has_key(other.projectName):
                otherCost[other.projectName] += other.cost #可能多个不同用途的同一个项目，计总和
            else:
                otherCost[other.projectName] = other.cost
            otherTotal += other.cost
        print u'其他费用合计/元（如短信）：', otherTotal
        print "*******************************************************"

        # fluxTotal = sum(list(Flux.objects.values_list('expense', flat=True)))*100
        fluxSet = Flux.objects.filter(month=self.month)
        fluxTotal = 0
        fluxCost = {}
        for flux in fluxSet:
            if fluxCost.has_key(flux.projectName):
                fluxCost[flux.projectName] += flux.expense
            else:
                fluxCost[flux.projectName] = flux.expense
            fluxTotal += flux.expense
        print u'流量费用合计/元：',fluxTotal

        print u"*****************资源账单/分**********************************"
        summ_ = -sum(list(QcloudDeal.objects.filter(month=self.month).values_list('amount', flat=True))) #所有费用
        projectSet = Project.objects.all()
        projectCost = {}
        summ = 0
        defaultCost = 0  # 默认项目费用+公司公共的费用
        for pro in projectSet:
            cost = -sum(list(QcloudDeal.objects.filter(month=self.month).filter(projectId=pro.projectId).values_list('amount', flat=True)))
            if pro.projectId in ('0', '1039043', '1042943'):
                defaultCost += cost
            else:
                projectCost[pro.projectName] = cost
                print pro.projectName, '    ', cost
            summ += cost
        print "*******************************************************"
        print u'默认项目+公司公共：', defaultCost
        print u'实际所有费用：', summ_, u'每个项目相加所有费用：',summ
        summ = summ_

        print "*******************************************************"
        print defaultCost, fluxTotal*100, otherTotal*100

        cdnTotal = -sum(list(QcloudDeal.objects.filter(Q(productCode='cdn') & Q(month=self.month)).values_list('amount', flat=True)))
        print u'cdn费用合计/分：', cdnTotal
        cdnCost = {}
        cdnSet = CdnPercentage.objects.filter(month=self.month)
        for cdn in cdnSet:
            cdnCost[cdn.projectName] = round(cdnTotal*cdn.percentage, 2)
            print cdn.projectName, round(cdnTotal*cdn.percentage, 2)

        print u"***********************项目费用明细/元****************************"
        print u'项目         账单费用      流量       cdn           短信        合计'
        qcloudStatistic = {}
        allProjectCost = 0
        for key in projectCost.keys():
            flag = True
            if fluxCost.has_key(key) and cdnCost.has_key(key) and otherCost.has_key(key):
                pro = round(projectCost[key]/100.0+fluxCost[key]+cdnCost[key]/100.0+otherCost[key], 2)
                # allProjectCost += pro
                # qcloudStatistic[key] = pro
                print key,'  ',projectCost[key]/100.0,'  ',fluxCost[key],'  ',cdnCost[key]/100.0,'  ',otherCost[key], pro
            elif fluxCost.has_key(key) and cdnCost.has_key(key):
                pro = round(projectCost[key]/100.0+fluxCost[key]+cdnCost[key]/100.0, 2)
                # allProjectCost += pro
                # qcloudStatistic[key] = pro
                print key,'  ',projectCost[key]/100.0,'  ',fluxCost[key],'  ',cdnCost[key]/100.0, ' 0 ', pro
            elif fluxCost.has_key(key):
                pro = round(projectCost[key]/100.0+fluxCost[key], 2)
                # allProjectCost += pro
                # qcloudStatistic[key] = pro
                print key,'  ',projectCost[key]/100.0,'  ',fluxCost[key], ' 0 ', ' 0 ', pro
            else:
                pro = round(projectCost[key]/100.0, 2)
                flag = False
                print key,'     ',projectCost[key]/100.0,'   ',' 0 ',' 0 ',' 0 ', pro
            if flag:
                allProjectCost += pro
                qcloudStatistic[key] = pro

        print u"********************项目费用合计******************************"
        for key in qcloudStatistic.keys():
            print key,'   ',qcloudStatistic[key]
        print "*******************************************************"
        summ = summ/100.0
        print u'所有项目费用：', allProjectCost
        commonCost = summ - allProjectCost
        print u'运维管理，网站论坛，预留资源：', commonCost
        print u'所有费用：', summ
        # 公司公共即是公共费用
        qcloudStatistic[u'公司公共'] = commonCost
        qcloudStatistic[u'所有费用'] = summ
        return qcloudStatistic

    def other_plat_cost(self, platName):
        if platName == 'all':
            OtherPlatSet = OtherPlatCost.objects.filter(month=self.month)
        else:
            OtherPlatSet = OtherPlatCost.objects.filter(Q(month=self.month) & Q(plat=platName))
        OtherPlatStatistic = {}
        for other in OtherPlatSet:
            plat = other.plat
            if not OtherPlatStatistic.has_key(plat):
                OtherPlatStatistic[plat] = {}
            OtherPlatStatistic[plat][other.projectName] = other.cost
        return OtherPlatStatistic

    def chinaShareCost(self, projects, qcloudData, otherPlatData):
        # otherPlatName = otherPlatData.keys()
        allProject = {}
        for pro in projects:
            allProject[pro] = 0
            if qcloudData.has_key(pro):
                allProject[pro] += qcloudData[pro]
            # for name in otherPlatName:
            #     if otherPlatData[name].has_key(pro):
            #         allProject[pro] += otherPlatData[name][pro]

            if otherPlatData.has_key(u'阿里云') and otherPlatData[u'阿里云'].has_key(pro):
                allProject[pro] += otherPlatData[u'阿里云'][pro]
            if otherPlatData.has_key(u'兆维') and otherPlatData[u'兆维'].has_key(pro):
                allProject[pro] += otherPlatData[u'兆维'][pro]
            if otherPlatData.has_key(u'鲁谷') and otherPlatData[u'鲁谷'].has_key(pro):
                allProject[pro] += otherPlatData[u'鲁谷'][pro]
            if otherPlatData.has_key('ucloud') and otherPlatData['ucloud'].has_key(pro):
                allProject[pro] += otherPlatData['ucloud'][pro]
        # 公共分摊
        common = allProject[u'公司公共']
        commonShare = {}
        if common != 0:
            allProject.pop(u'公司公共')
            total = sum(allProject.values())
            deviation = 0
            for key in allProject.keys():
                percentage = allProject[key]/total
                share = round(common * percentage, 2)
                allProject[key] += share
                commonShare[key] = share
                deviation += share
            # 因为保留两位小数，所以存在很小的误差，将误差计入某一个项目
            key = commonShare.keys()[0]
            commonShare[key] += common - deviation
            allProject[key] += common - deviation
        # 平台支撑，大数据分摊
        plat = allProject[u'平台支撑']
        bigData = allProject[u'大数据']
        allProject.pop(u'平台支撑')
        allProject.pop(u'大数据')
        print u'**************************************'
        print u'平台支撑：', plat, u'大数据', bigData
        platShare = {}
        bigDataShare = {}
        deviation1 = 0
        deviation2 = 0
        for key in allProject.keys():
            platSet = Plat.objects.filter(month=self.month).filter(version=u'大陆').filter(projectName=key)
            if platSet:
                share = round(plat * platSet[0].percentage, 2)
                platShare[key] = share
                allProject[key] += share
                key1 = key
                deviation1 += share
            bigDataSet = BigData.objects.filter(month=self.month).filter(version=u'大陆').filter(projectName=key)
            if bigDataSet:
                share = round(bigData * bigDataSet[0].percentage, 2)
                bigDataShare[key] = share
                allProject[key] += share
                deviation2 += share
        platShare[key1] += plat - deviation1
        allProject[key1] += plat - deviation1
        # 大数据费用是由国内外共同分摊的
        awsBigDataCost = bigData - deviation2
        print u'海外的大数据费用：', awsBigDataCost

        for key in platShare.keys():
            print key,platShare[key]

        return commonShare, platShare, bigDataShare, allProject, bigData, awsBigDataCost

    def awsShareCost(self, bigData, awsBigDataCost):
        awsSet = AwsCost.objects.filter(month=self.month)
        awsCost = {}
        awsSum = 0
        for aws in awsSet:
            project = '+'.join([aws.projectName, aws.region, aws.version])
            summ = round(aws.serviceCost+aws.supportCost,2)
            if aws.projectName == u'平台支撑':
                platCost = summ
                awsCost[project] = [round(aws.serviceCost,2), round(aws.supportCost,2), 0]
                continue
            if aws.projectName == u'公司公共':
                commonCost = summ
                awsCost[project] = [round(aws.serviceCost,2), round(aws.supportCost,2), 0]
                continue
            awsCost[project] = [round(aws.serviceCost,2), round(aws.supportCost,2), summ]
            # if aws.projectName not in (u'平台支撑', u'公司公共'):
            awsSum += summ
        # 公共分摊
        commonShare = {}
        deviation = 0
        for key in awsCost.keys():
            if (u'平台支撑' in key) or (u'公司公共' in key):
                continue
            percentage = awsCost[key][2]/awsSum
            share = round(commonCost * percentage, 2)
            commonShare[key] = share
            deviation += share
            awsCost[key][2] += share
        key = commonShare.keys()[0]
        commonShare[key] += commonCost - deviation
        awsCost[key][2] += commonCost - deviation

        # 平台分摊
        platSet = Plat.objects.filter(month=self.month).exclude(version=u'大陆')
        platShare = {}
        deviation = 0
        for plat in platSet:
            project = '+'.join([plat.projectName, plat.region, plat.version])
            share = round(platCost * plat.percentage, 2)
            platShare[project] = share
            deviation += share
            awsCost[project][2] += share
        key = platShare.keys()[0]
        platShare[key] += platCost - deviation
        awsCost[key][2] += platCost - deviation

        # 大数据分摊
        bigDataSet = BigData.objects.filter(month=self.month).exclude(version=u'大陆').exclude(percentage=0)
        # 由于汇率问题，存在微小误差，汇率为 6.9
        bigData = round(bigData/6.9, 2)
        awsBigDataCost = round(awsBigDataCost/6.9, 2)
        bigDataShare = {}
        deviation = 0
        for data in bigDataSet:
            project = '+'.join([data.projectName, data.region, data.version])
            share = round(bigData * data.percentage, 2)
            bigDataShare[project] = share
            deviation += share
            awsCost[project][2] += share
        key = bigDataShare.keys()[0]
        bigDataShare[key] += awsBigDataCost - deviation
        awsCost[key][2] += awsBigDataCost - deviation

        for key in platShare.keys():
            print key,platShare[key]

        return awsCost, commonShare, platShare, bigDataShare

    def costData(self, paltName):
        # 所有平台的项目: 腾讯云+其他平台
        projectSet1 = list(Project.objects.exclude(Q(projectId='0') | Q(projectId='1042943')).values_list('projectName', flat=True))
        projectSet2 = list(set(OtherPlatCost.objects.filter(month=self.month).values_list('projectName', flat=True)))
        projects = list(set(projectSet1 + projectSet2))

        if paltName == 'all':
            qcloudData = self.qcloud_project_cost()
            otherPlatData = self.other_plat_cost(paltName)
        elif paltName == 'qcloud':
            qcloudData = self.qcloud_project_cost()
            otherPlatData = {}
        else:
            qcloudData = {}
            otherPlatData = self.other_plat_cost(paltName)
            if otherPlatData == {}:
                return False
        try:
            commonShare, platShare, bigDataShare, allProject, bigData, awsBigDataCost = self.chinaShareCost(projects, qcloudData, otherPlatData)
        except:
            return {'data':'没有原始数据，无法计算!'}

        chinaCostApi = {}
        awsCostApi = {}
        projects.remove(u'公司公共')
        projects.remove(u'平台支撑')
        projects.remove(u'大数据')
        projects.append(u'大数据')
        projects.append(u'平台支撑')
        projects.append(u'公司公共')

        for pro in projects:
            chinaCostApi[pro] = {}
            chinaCostApi[pro][u'发行区域'] = u'发行一部'
            chinaCostApi[pro][u'版本'] = u'大陆'
            if qcloudData.has_key(pro):
                chinaCostApi[pro]['qcloud'] = round(qcloudData[pro], 2)
            else:
                chinaCostApi[pro]['qcloud'] = 0
            if otherPlatData.has_key(u'阿里云') and otherPlatData[u'阿里云'].has_key(pro):
                chinaCostApi[pro][u'阿里云'] = round(otherPlatData[u'阿里云'][pro], 2)
            else:
                chinaCostApi[pro][u'阿里云'] = 0
            if otherPlatData.has_key(u'兆维') and otherPlatData[u'兆维'].has_key(pro):
                chinaCostApi[pro][u'兆维'] = round(otherPlatData[u'兆维'][pro], 2)
            else:
                chinaCostApi[pro][u'兆维'] = 0
            if otherPlatData.has_key(u'鲁谷') and otherPlatData[u'鲁谷'].has_key(pro):
                chinaCostApi[pro][u'鲁谷'] = round(otherPlatData[u'鲁谷'][pro], 2)
            else:
                chinaCostApi[pro][u'鲁谷'] = 0
            if otherPlatData.has_key('ucloud') and otherPlatData['ucloud'].has_key(pro):
                chinaCostApi[pro]['ucloud'] = round(otherPlatData['ucloud'][pro], 2)
            else:
                chinaCostApi[pro][u'ucloud'] = 0
            if commonShare.has_key(pro):
                chinaCostApi[pro][u'公司公共'] = round(commonShare[pro], 2)
            else:
                chinaCostApi[pro][u'公司公共'] = 0
            if platShare.has_key(pro):
                chinaCostApi[pro][u'平台支撑'] = round(platShare[pro], 2)
            else:
                chinaCostApi[pro][u'平台支撑'] = 0
            if bigDataShare.has_key(pro):
                chinaCostApi[pro][u'大数据'] = round(bigDataShare[pro], 2)
            else:
                chinaCostApi[pro][u'大数据'] = 0
            if allProject.has_key(pro):
                chinaCostApi[pro][u'项目总额(元)'] = round(allProject[pro], 2)
            else:
                chinaCostApi[pro][u'项目总额(元)'] = 0
        chinaCostApi = sorted(chinaCostApi.iteritems(), key=lambda d:d[1][u'项目总额(元)'], reverse = True)

        if paltName in ('all', '兆维'):
            try:
                awsCost, commonShare_, platShare_, bigDataShare_ = self.awsShareCost(bigData, awsBigDataCost)
            except:
                return {'data':'没有原始数据，无法计算!'}
            projects = []
            other = []
            for key in awsCost.keys():
                if (u'平台支撑' in key) or (u'公司公共' in key):
                    other.append(key)
                    continue
                projects.append(key)
            projects += other
            for pro in projects:
                awsCostApi[pro] = {}
                awsCostApi[pro][u'服务费用'] = round(awsCost[pro][0], 2)
                awsCostApi[pro][u'支持费用'] = round(awsCost[pro][1], 2)
                if commonShare_.has_key(pro):
                    awsCostApi[pro][u'公司公共'] = round(commonShare_[pro], 2)
                else:
                    awsCostApi[pro][u'公司公共'] = 0
                if platShare_.has_key(pro):
                    awsCostApi[pro][u'平台支撑'] = round(platShare_[pro], 2)
                else:
                    awsCostApi[pro][u'平台支撑'] = 0
                if bigDataShare_.has_key(pro):
                    awsCostApi[pro][u'大数据'] = round(bigDataShare_[pro], 2)
                else:
                    awsCostApi[pro][u'大数据'] = 0
                awsCostApi[pro][u'项目总额(美元)'] = round(awsCost[pro][2], 2)
            awsCostApi = sorted(awsCostApi.iteritems(), key=lambda d:d[1][u'项目总额(美元)'], reverse = True)
            awsCostApi_ = []
            for project in awsCostApi:
                temp = []
                temp += project[0].split('+')
                temp.append(project[1])
                awsCostApi_.append(temp)
            costApi = {'chinaCostApi': chinaCostApi, 'awsCostApi': awsCostApi_}
            return costApi
        return chinaCostApi

    # 后台测试
    def fortest(self, paltName):
        costApi = self.costData(paltName)
        if paltName=='all':
            for pro in costApi['chinaCostApi']:
                print pro[0], pro[1][u'发行区域'], pro[1][u'版本'],pro[1]['qcloud'],pro[1][u'阿里云'],pro[1][u'兆维'],\
                    pro[1][u'鲁谷'],pro[1]['ucloud'],pro[1][u'公司公共'],pro[1][u'平台支撑'], pro[1][u'大数据'],pro[1][u'项目总额(元)']
            for pro in costApi['awsCostApi']:
                print pro[0],pro[1],pro[2],pro[3][u'服务费用'],pro[3][u'支持费用'],pro[3][u'公司公共'],\
                        pro[3][u'平台支撑'],pro[3][u'大数据'],pro[3][u'项目总额(美元)']
        else:
            if costApi:
                for pro in costApi:
                    print pro[0], pro[1][u'发行区域'], pro[1][u'版本'],pro[1]['qcloud'],pro[1][u'阿里云'],pro[1][u'兆维'],\
                        pro[1][u'鲁谷'],pro[1]['ucloud'],pro[1][u'公司公共'],pro[1][u'平台支撑'], pro[1][u'大数据'],pro[1][u'项目总额(元)']
            else:
                print u'该平台没有数据或者已经下架！'


    def save_cost_to_db(self):
        costApi = self.costData('all')
        if not costApi.has_key('chinaCostApi'):
            return costApi
        chinaCostApi = costApi['chinaCostApi']
        awsCostApi = costApi['awsCostApi']
        if not ChinaPerMonthCost.objects.filter(month=self.month):
            for pro in chinaCostApi:
                ChinaPerMonthCost.objects.create(projectName=pro[0],
                                                region=pro[1][u'发行区域'],
                                                version=pro[1][u'版本'],
                                                qcloud=pro[1]['qcloud'],
                                                ali=pro[1][u'阿里云'],
                                                zhaowei=pro[1][u'兆维'],
                                                lugu=pro[1][u'鲁谷'],
                                                ucloud=pro[1]['ucloud'],
                                                common=pro[1][u'公司公共'],
                                                plat=pro[1][u'平台支撑'],
                                                bigData=pro[1][u'大数据'],
                                                total=pro[1][u'项目总额(元)'],
                                                month=self.month
                                                )
        if not OverseasPerMonthCost.objects.filter(month=self.month):
            for pro in awsCostApi:
                OverseasPerMonthCost.objects.create(projectName=pro[0],
                                                region=pro[1],
                                                version=pro[2],
                                                service=pro[3][u'服务费用'],
                                                support=pro[3][u'支持费用'],
                                                common=pro[3][u'公司公共'],
                                                plat=pro[3][u'平台支撑'],
                                                bigData=pro[3][u'大数据'],
                                                total=pro[3][u'项目总额(美元)'],
                                                month=self.month
                                                )
        qcloudCostApi = self.costData('qcloud')
        if not QcloudCost.objects.filter(month=self.month):
            for pro in qcloudCostApi:
                if pro[1]['qcloud'] + pro[1][u'项目总额(元)'] == 0:
                    continue
                QcloudCost.objects.create(projectName=pro[0],
                                          region=pro[1][u'发行区域'],
                                          version=pro[1][u'版本'],
                                          qcloud=pro[1]['qcloud'],
                                          common=pro[1][u'公司公共'],
                                          plat=pro[1][u'平台支撑'],
                                          total=pro[1][u'项目总额(元)'],
                                          month=self.month
                                          )
        aliCostApi = self.costData('阿里云')
        if not AliCost.objects.filter(month=self.month) and aliCostApi:
            for pro in aliCostApi:
                if pro[1][u'阿里云'] + pro[1][u'项目总额(元)'] == 0:
                    continue
                AliCost.objects.create(projectName=pro[0],
                                        region=pro[1][u'发行区域'],
                                        version=pro[1][u'版本'],
                                        ali=pro[1][u'阿里云'],
                                        common=pro[1][u'公司公共'],
                                        plat=pro[1][u'平台支撑'],
                                        total=pro[1][u'项目总额(元)'],
                                        month=self.month
                                        )

        costApi = self.costData('兆维')
        if costApi:
            zhaoweicostApi = costApi['chinaCostApi']
            awsCostApi = costApi['awsCostApi']
            if not ZhaoWeiCost.objects.filter(month=self.month):
                for pro in zhaoweicostApi:
                    if pro[1][u'兆维'] + pro[1][u'项目总额(元)'] == 0:
                        continue
                    ZhaoWeiCost.objects.create(projectName=pro[0],
                                            region=pro[1][u'发行区域'],
                                            version=pro[1][u'版本'],
                                            zhaowei=pro[1][u'兆维'],
                                            common=pro[1][u'公司公共'],
                                            plat=pro[1][u'平台支撑'],
                                            bigData=pro[1][u'大数据'],
                                            total=pro[1][u'项目总额(元)'],
                                            month=self.month
                                            )
            if not AwsShareCost.objects.filter(month=self.month):
                for pro in awsCostApi:
                    AwsShareCost.objects.create(projectName=pro[0],
                                                region=pro[1],
                                                version=pro[2],
                                                service=pro[3][u'服务费用'],
                                                support=pro[3][u'支持费用'],
                                                common=pro[3][u'公司公共'],
                                                plat=pro[3][u'平台支撑'],
                                                bigData=pro[3][u'大数据'],
                                                total=pro[3][u'项目总额(美元)'],
                                                month=self.month
                                                )
        luguCostApi = self.costData('鲁谷')
        if not LuGuCost.objects.filter(month=self.month) and luguCostApi and isinstance(luguCostApi,list):
            for pro in luguCostApi:
                if pro[1][u'鲁谷'] + pro[1][u'项目总额(元)'] == 0.0:
                    continue
                LuGuCost.objects.create(projectName=pro[0],
                                        region=pro[1][u'发行区域'],
                                        version=pro[1][u'版本'],
                                        lugu=pro[1][u'鲁谷'],
                                        common=pro[1][u'公司公共'],
                                        plat=pro[1][u'平台支撑'],
                                        total=pro[1][u'项目总额(元)'],
                                        month=self.month
                                        )
        ucloudCostApi = self.costData('ucloud')
        if not UcloudCost.objects.filter(month=self.month) and ucloudCostApi:
            for pro in ucloudCostApi:
                if pro[1][u'ucloud'] + pro[1][u'项目总额(元)'] == 0.0:
                    continue
                UcloudCost.objects.create(projectName=pro[0],
                                        region=pro[1][u'发行区域'],
                                        version=pro[1][u'版本'],
                                        ucloud=pro[1][u'ucloud'],
                                        common=pro[1][u'公司公共'],
                                        plat=pro[1][u'平台支撑'],
                                        total=pro[1][u'项目总额(元)'],
                                        month=self.month
                                        )
        return {'data':'当月成本计算完成！'}

# 被costApi调用
def exportExcel(chinaCostApi, awsCostApi, qcloudCostApi, aliCostApi, \
                zhaoweicostApi, luguCostApi, ucloudCostApi, awsShareCostApi, currentMonth):
    # 创建excel
    workbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = workbook.add_sheet(u'大陆项目费用总计')
    # title = [u'项目',u'发行区域',u'版本',u'平台',u'项目分摊',u'项目总额(元)']
    # titleSmall1 = [u'qcloud',u'阿里云',u'兆维',u'鲁谷']
    # titleSmall2 = [u'公司公共',u'平台支撑',u'大数据']
    title = [u'项目',u'发行区域',u'版本',u'qcloud',u'阿里云',u'兆维',u'鲁谷','ucloud',u'公司公共',u'平台支撑',u'大数据',u'项目总额(元)']
    # length1 = len(titleSmall1)
    # length2 = len(titleSmall2)
    for i in range(0,len(title)):
        worksheet.col(i).width=256*20
        worksheet.write_merge(0,1,i,i,title[i],get_sheet_title_style())
        # if i == 3:
        #     col = i #col代表列位置
        #     worksheet.write_merge(0,0,col,col+length1-1,title[i], get_sheet_title_style())
        #     for j in range(0, length1):
        #         worksheet.col(col+j).width=256*20
        #         worksheet.write(1,col+j,titleSmall1[j], get_sheet_title_style())
        # elif i == 4:
        #     col = i+length1-1
        #     worksheet.write_merge(0,0,col,col+length2-1,title[i], get_sheet_title_style())
        #     for k in range(0, length2):
        #         worksheet.col(col+k).width=256*20
        #         worksheet.write(1,col+k,titleSmall2[k], get_sheet_title_style())
        # elif i > 4:
        #     col = i+length1-1+length2-1
        #     worksheet.col(col).width=256*20
        #     worksheet.write_merge(0,1,col,col,title[i],get_sheet_title_style())
        # else:
        #     worksheet.col(i).width=256*20
        #     worksheet.write_merge(0,1,i,i,title[i],get_sheet_title_style())
    row = 2
    for pro in chinaCostApi:
        worksheet.write(row,0,pro['projectName'], get_body_title_style())
        worksheet.write(row,1,pro['region'], get_body_title_style())
        worksheet.write(row,2,pro['version'], get_body_title_style())
        worksheet.write(row,3,pro['qcloud'], get_body_title_style())
        worksheet.write(row,4,pro['ali'], get_body_title_style())
        worksheet.write(row,5,pro['zhaowei'], get_body_title_style())
        worksheet.write(row,6,pro['lugu'], get_body_title_style())
        worksheet.write(row,7,pro['ucloud'], get_body_title_style())
        worksheet.write(row,8,pro['common'], get_body_title_style())
        worksheet.write(row,9,pro['plat'], get_body_title_style())
        worksheet.write(row,10,pro['bigData'], get_body_title_style())
        worksheet.write(row,11,pro['total'], get_body_title_style())
        row += 1

    worksheet = workbook.add_sheet(u'海外项目费用总计')
    # title = [u'项目',u'发行区域',u'版本',u'服务费用',u'支持费用',u'项目分摊',u'项目总额(美元)']
    title = [u'项目',u'发行区域',u'版本',u'服务费用',u'支持费用',u'公司公共',u'平台支撑',u'大数据',u'项目总额(美元)']
    # length = len(titleSmall2)
    for i in range(0,len(title)):
        worksheet.col(i).width=256*20
        worksheet.write_merge(0,1,i,i,title[i],get_sheet_title_style())
        # if i == 5:
        #     col = i
        #     worksheet.write_merge(0,0,col,col+length-1,title[i], get_sheet_title_style())
        #     for j in range(0, length):
        #         worksheet.col(col+j).width=256*20
        #         worksheet.write(1,col+j,titleSmall2[j], get_sheet_title_style())
        # elif i > 5:
        #     col = i+length-1
        #     worksheet.col(col).width=256*20
        #     worksheet.write_merge(0,1,col,col,title[i],get_sheet_title_style())
        # else:
        #     worksheet.col(i).width=256*20
        #     worksheet.write_merge(0,1,i,i,title[i],get_sheet_title_style())
    row = 2
    for pro in awsCostApi:
        worksheet.write(row,0,pro['projectName'], get_body_title_style())
        worksheet.write(row,1,pro['region'], get_body_title_style())
        worksheet.write(row,2,pro['version'], get_body_title_style())
        worksheet.write(row,3,pro[u'service'], get_body_title_style())
        worksheet.write(row,4,pro[u'support'], get_body_title_style())
        worksheet.write(row,5,pro[u'common'], get_body_title_style())
        worksheet.write(row,6,pro[u'plat'], get_body_title_style())
        worksheet.write(row,7,pro[u'bigData'], get_body_title_style())
        worksheet.write(row,8,pro[u'total'], get_body_title_style())
        row += 1

    worksheet = workbook.add_sheet(u'qcloud项目费用合计')
    title = [u'项目',u'发行区域',u'版本',u'qcloud',u'公司公共',u'平台支撑',u'项目总额(元)']
    for i in range(0,len(title)):
        worksheet.col(i).width=256*20
        worksheet.write_merge(0,1,i,i,title[i],get_sheet_title_style())
    row = 2
    for pro in qcloudCostApi:
        worksheet.write(row,0,pro['projectName'], get_body_title_style())
        worksheet.write(row,1,pro['region'], get_body_title_style())
        worksheet.write(row,2,pro['version'], get_body_title_style())
        worksheet.write(row,3,pro['qcloud'], get_body_title_style())
        worksheet.write(row,4,pro['common'], get_body_title_style())
        worksheet.write(row,5,pro['plat'], get_body_title_style())
        worksheet.write(row,6,pro['total'], get_body_title_style())
        row += 1

    if aliCostApi:
        worksheet = workbook.add_sheet(u'阿里云项目费用合计')
        title = [u'项目',u'发行区域',u'版本',u'阿里云',u'公司公共',u'平台支撑',u'项目总额(元)']
        for i in range(0,len(title)):
            worksheet.col(i).width=256*20
            worksheet.write_merge(0,1,i,i,title[i],get_sheet_title_style())
        row = 2
        for pro in aliCostApi:
            worksheet.write(row,0,pro['projectName'], get_body_title_style())
            worksheet.write(row,1,pro['region'], get_body_title_style())
            worksheet.write(row,2,pro['version'], get_body_title_style())
            worksheet.write(row,3,pro['ali'], get_body_title_style())
            worksheet.write(row,4,pro['common'], get_body_title_style())
            worksheet.write(row,5,pro['plat'], get_body_title_style())
            worksheet.write(row,6,pro['total'], get_body_title_style())
            row += 1
    if zhaoweicostApi:
        worksheet = workbook.add_sheet(u'兆维项目费用合计')
        title = [u'项目',u'发行区域',u'版本',u'兆维',u'公司公共',u'平台支撑',u'大数据',u'项目总额(元)']
        for i in range(0,len(title)):
            worksheet.col(i).width=256*20
            worksheet.write_merge(0,1,i,i,title[i],get_sheet_title_style())
        row = 2
        for pro in zhaoweicostApi:
            worksheet.write(row,0,pro['projectName'], get_body_title_style())
            worksheet.write(row,1,pro['region'], get_body_title_style())
            worksheet.write(row,2,pro['version'], get_body_title_style())
            worksheet.write(row,3,pro['zhaowei'], get_body_title_style())
            worksheet.write(row,4,pro['common'], get_body_title_style())
            worksheet.write(row,5,pro['plat'], get_body_title_style())
            worksheet.write(row,6,pro['bigData'], get_body_title_style())
            worksheet.write(row,7,pro['total'], get_body_title_style())
            row += 1
    if luguCostApi:
        worksheet = workbook.add_sheet(u'鲁谷项目费用合计')
        title = [u'项目',u'发行区域',u'版本',u'鲁谷',u'公司公共',u'平台支撑',u'项目总额(元)']
        for i in range(0,len(title)):
            worksheet.col(i).width=256*20
            worksheet.write_merge(0,1,i,i,title[i],get_sheet_title_style())
        row = 2
        for pro in luguCostApi:
            worksheet.write(row,0,pro['projectName'], get_body_title_style())
            worksheet.write(row,1,pro['region'], get_body_title_style())
            worksheet.write(row,2,pro['version'], get_body_title_style())
            worksheet.write(row,3,pro['lugu'], get_body_title_style())
            worksheet.write(row,4,pro['common'], get_body_title_style())
            worksheet.write(row,5,pro['plat'], get_body_title_style())
            worksheet.write(row,6,pro['total'], get_body_title_style())
            row += 1
    if ucloudCostApi:
        worksheet = workbook.add_sheet(u'ucloud项目费用合计')
        title = [u'项目',u'发行区域',u'版本','ucloud',u'公司公共',u'平台支撑',u'项目总额(元)']
        for i in range(0,len(title)):
            worksheet.col(i).width=256*20
            worksheet.write_merge(0,1,i,i,title[i],get_sheet_title_style())
        row = 2
        for pro in ucloudCostApi:
            worksheet.write(row,0,pro['projectName'], get_body_title_style())
            worksheet.write(row,1,pro['region'], get_body_title_style())
            worksheet.write(row,2,pro['version'], get_body_title_style())
            worksheet.write(row,3,pro['ucloud'], get_body_title_style())
            worksheet.write(row,4,pro['common'], get_body_title_style())
            worksheet.write(row,5,pro['plat'], get_body_title_style())
            worksheet.write(row,6,pro['total'], get_body_title_style())
            row += 1
    if awsShareCostApi:
        worksheet = workbook.add_sheet(u'AWS项目费用合计')
        title = [u'项目',u'发行区域',u'版本',u'服务费用',u'支持费用',u'公司公共',u'平台支撑',u'大数据',u'项目总额(美元)']
        for i in range(0,len(title)):
            worksheet.col(i).width=256*20
            worksheet.write_merge(0,1,i,i,title[i],get_sheet_title_style())
        row = 2
        for pro in awsShareCostApi:
            worksheet.write(row,0,pro['projectName'], get_body_title_style())
            worksheet.write(row,1,pro['region'], get_body_title_style())
            worksheet.write(row,2,pro['version'], get_body_title_style())
            worksheet.write(row,3,pro[u'service'], get_body_title_style())
            worksheet.write(row,4,pro[u'support'], get_body_title_style())
            worksheet.write(row,5,pro[u'common'], get_body_title_style())
            worksheet.write(row,6,pro[u'plat'], get_body_title_style())
            worksheet.write(row,7,pro[u'bigData'], get_body_title_style())
            worksheet.write(row,8,pro[u'total'], get_body_title_style())
            row += 1
    fileName = 'operation/static/outfiles/'+currentMonth+'_cost_result.csv'
    workbook.save(fileName) #保存文件

if __name__ == '__main__':
    month = raw_input("input expense month: ")
    if not month:
        month = (datetime.date.today().replace(day=1) - datetime.timedelta(1)).strftime('%Y-%m')
    test = GetCost(month)
    test.save_cost_to_db()
