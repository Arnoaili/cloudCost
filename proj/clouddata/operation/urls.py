from django.conf.urls import include, url
from costApi import *
from uploadFile import *
from login import *

urlpatterns = [
    url(r'^auth/$', LoginView.as_view(), name='auth'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^user/$', CurrentUser.as_view(), name='user'),

    url(r'^chart/$', ChartView.as_view(), name='chart'),
    url(r'^$', CostView, name='cost'),
    url(r'^excel/$', GetExcel, name='exportExcel'),
    url(r'^syncqcloud/$', SyncQcloud, name='syncqcloud'),
    url(r'^calculate/$', Calculate, name='calculate'),
    url(r'^fluxapi/$', FluxCostView, name='fluxapi'),
    url(r'^platapi/$', PlatPercentageView, name='platapi'),
    url(r'^awsapi/$', AwsCostView, name='awsapi'),
    url(r'^qcloudothercostapi/$', QcloudOtherCostView, name='qcloudothercostapi'),
    url(r'^otherplatcostapi/$', OtherPlatCostView, name='otherplatcostapi'),
    url(r'^bigdataapi/$', BigDataPercentageView, name='bigdataapi'),

    url(r'^importfluxfile/$', UploadFluxFile, name='importfluxfile'),
    url(r'^importplatfile/$', UploadPlatFile, name='importplatfile'),
    url(r'^importawsfile/$', UploadAwsFile, name='importawsfile'),
    url(r'^importotherplatfile/$', UploadOtherPlatFile, name='importotherplatfile'),
    url(r'^importbigdatafile/$', UploadBigDataFile, name='importbigdatafile'),
    url(r'^importqcloudothercostfile/$', UploadQcloudOtherCostFile, name='importqcloudothercostfile'),
]
