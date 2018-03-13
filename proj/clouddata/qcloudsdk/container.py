#!/usr/bin/python
# -*- coding: utf-8 -*-
import json,urllib2
from src.QcloudApi.qcloudapi import QcloudApi
import datetime
import smtplib
from email.mime.text import MIMEText

instance_list = []

def get_overtime_containers(region, projectData):
    module = 'cvm'
    action = 'DescribeInstances'
    secretId = 'AKIDWxMDr345iqht1PJhXYi1k9zJ9khdvj1X'
    secretKey = 'R9PDuyIDLsLL8afFNX2wTFYQ13cdRvHh'
    config = {
        'Region': region,
        'secretId': secretId,
        'secretKey': secretKey,
        'method': 'get'
    }
    params = {
            'limit': 100,
            'Filters.1.Name': 'instance-charge-type',
            'Filters.1.Values.1': 'POSTPAID_BY_HOUR'}# 目前只查询按量付费的参数Filters没起作用
    global instance_list
    try:
        service = QcloudApi(module, config)
        # print service.generateUrl(action, params)
        data = json.loads(service.call(action, params))['instanceSet']
        now = datetime.datetime.now()
        for da in data:
            createTime = datetime.datetime.strptime(da['createTime'], '%Y-%m-%d %H:%M:%S')
            second = (now-createTime).total_seconds()
            # if createTime.strftime('%Y-%m-%d') == '2017-11-01' and second >= 1800:
            if da['cvmPayMode'] == 2 and createTime.strftime('%Y-%m-%d') == now.strftime('%Y-%m-%d') and second >= 1200:
                instance = {}
                print da['createTime'], da['instanceName'],da['unInstanceId'], int(second/60)
                for project in projectData['data']:
                    if project['projectId'] == da['projectId']:
                        instance['projectName'] = project['projectName']
                        break
                instance['instanceName'] = da['instanceName']
                instance['unInstanceId'] = da['unInstanceId']
                instance['createTime'] = da['createTime']
                instance['zoneName'] = da['zoneName']
                instance['timeCast'] = int(second/60)
                if instance['projectName'] != u'东京喰种':
                    instance_list.append(instance)
    except Exception, e:
        print 'exception:', e


def send_mail(content):
    mail_to = ['aili@digisky.com', 'liuyongsheng@digisky.com']
    sender = 'devops@digisky.com'
    username = 'devops@digisky.com'
    password = 'd1v0PS#,4'
    smtpserver = 'smtp.qiye.163.com'
    subject = u'qcloud容器定时检查 %s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = MIMEText(content, 'html', 'utf-8')
    msg['Subject'] = subject#Header(subject, 'utf-8')
    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(sender, mail_to, msg.as_string())
    smtp.quit()

def main():
    url = 'http://cost.digi-sky.com/q/v1/project/'
    projectData = json.loads(urllib2.urlopen(url).read())
    regions = ['bj', 'sh', 'gz', 'cd']
    for region in regions:
        get_overtime_containers(region, projectData)
    if instance_list:
        html = u'''
            <html>
            <head>
            <style type="text/css">
            table, th, td {
              border: 1px solid #ddd;
            }
            .mail_table {
              width: 100%;
              max-width: 100%;
              margin-bottom: 20px;
              border: 1px solid #dddddd;
              border-collapse: collapse;
              border-spacing: 0;
            }
            .mail_table > tr:hover {
              background-color: #f5f5f5;
            }
            </style>
            </head>
            <body>
                <p>以下是运行时间大于20分钟的容器：</p>
                <table class="mail_table">
                <tr>
                    <th>主机名</th>
                    <th>ID</th>
                    <th>项目名</th>
                    <th>区域</th>
                    <th>创建时间</th>
                    <th>使用时间(分)</th>
                </tr>
            '''
        for instance in instance_list:
            html += '<tr>'
            html += '<td align="center">%s</td>' % instance['instanceName']
            html += '<td align="center">%s</td>' % instance['unInstanceId']
            html += '<td align="center">%s</td>' % instance['projectName']
            html += '<td align="center">%s</td>' % instance['zoneName']
            html += '<td align="center">%s</td>' % instance['createTime']
            html += '<td align="center">%s</td>' % instance['timeCast']
            html += '</tr>'
        html += '</table>'
        html += u'<h4>总计：%s台</h4><br><br>' % len(instance_list)
        html += '<p><font color="gray"><hr  align="left" width="30%">'
        html += u'运维支撑部<br />'
        html += u'成都数字天空科技有限公司<br />'
        html += '</font></p>'
        html += '</body>'
        html += '</html>'

        send_mail(html)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print '*******************', 'Send mail successful at ', now, '*******************'


if __name__ == '__main__':
    main()
