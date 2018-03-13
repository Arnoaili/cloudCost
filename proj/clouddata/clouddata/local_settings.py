# coding=utf8
__author__ = 'aili@digisky.com'

"""
Django settings for qcloudapi project.

"""

SECRETID = 'AKIDWxMDr345iqht1PJhXYi1k9zJ9khdvj1X'
SECRETKEY = 'R9PDuyIDLsLL8afFNX2wTFYQ13cdRvHh'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'expense',
        'USER': 'root',
        'PASSWORD': 'admin1',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

LDAP_UTL = "ldap://ipa.digi-sky.com:389"
LDAP_BIND_DN = "uid=servercost,cn=users,cn=accounts,dc=digisky,dc=com"
LDAP_PASSWORD = "4BF8VRMdINFUPUI"
