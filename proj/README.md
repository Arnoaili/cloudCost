# 成本计算，查询系统
# 项目主要功能
项目基于Django搭建，主要实现一下功能：
    
（1）云服务中间件

    * http://192.168.80.20:2000/q/v1/project/   查询所有项目（get请求）
    * http://192.168.80.20:2000/q/v1/region/    查询区域（get请求），请求方法如下：
    
    import requests
    r = requests.get('http://127.0.0.1:8000/q/v1/project/')
    print r.json()
    
    * http://192.168.80.20:2000/q/v1/{region}/{module}/  查询所有实例，请求方法如下：
    
    import requests
    data = {'region':'bj', 'moduel':'cdb', 'action':'DescribeCdbInstances'}
    r = requests.post('http://127.0.0.1:8000/q/v1/instances/', data=data)
    print r.json()
        	
（2）检查腾讯云容器的运行时间，大于30分钟邮件报警，在服务器上做crontab定时任务;

（3）腾讯云成本分析查询接口，按月查询每个项目的成本数据；

（4）通过页面查看平台，流量比例数据，可导入excel数据，修改，添加，新建数据。


# 项目使用注意事项
  * 腾讯云流量费用，腾讯云其他费用（如短信），海内外平台分摊比例，海外费用，大数据分摊比例，阿里云/兆维/鲁谷费用，这些数据需要通过6个excel导入数据到mysql；
  * 以上所有excel的项目名称以腾讯云为准，主要差别为：王道，百日公主，东京喰种，大数据，不能为王道三国，100日公主，东京战纪，平台数据；

# 成本计算流程
  * 大陆
    * qcloud
        * 资源账单 = 当月预付费+当月后付费（除去截止上月最后一天的部分）-当月退款+下月后付费（截止当月最后一天的部分）
        * 项目费用 = 资源账单+流量+cdn+其他费用（如短信），其中流量和其他费用由excel表导入
        * 公司公共（包括默认项目和公司公共）= qcloud所有费用 - 项目费用
    * 阿里云/兆维/鲁谷
        * 所有项目费用由excel表导入

  * 海外
    * AWS
        * 所有项目费用由excel表导入

  * 项目分摊
    * 公共分摊
        * 根据各个项目的费用占比进行分摊，即 大陆所有平台的单个项目费用和/大陆所有平台所有项目费用和；海外分摊比例同理计算
    * 平台分摊
        * 分摊比例由excel表导入，包括大陆和海外的数据，各自分摊大陆和海外的费用
    * 大数据分摊
        * 分摊比例由excel表导入，大陆和海外总占比为1，费用由海内外共同分摊 
    
  * 成本计算方式分为两种：
    * （1）海内外项目费用总计---用于记录历史数据，统计
    * （2）qcloud，ali，兆维，鲁谷，aws 各个平台单独费用合计---用于报账
    *  因为公司公共分摊是按各个项目的费用占比进行分摊的，所以上述两种计算方式分摊数据不同。
    
