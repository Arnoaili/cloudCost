#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def login(request):
    return render(request, 'login.html')

@login_required(login_url='/login')
def index(request):
    return render(request, 'index.html')

@login_required
def search(request):
    return render(request, 'search.html')

@login_required
def syncQcloud(request):
    return render(request, 'qclouddata.html')

@login_required
def fluxpercentage(request):
    return render(request, 'fluxpercentage.html')

@login_required
def platpercentage(request):
    return render(request, 'platpercentage.html')

@login_required
def awsCost(request):
    return render(request, 'awsCost.html')

@login_required
def qcloudOtherCost(request):
    return render(request, 'qcloudOtherCost.html')

@login_required
def otherPlatCost(request):
    return render(request, 'otherPlatCost.html')

@login_required
def bigData(request):
    return render(request, 'bigData.html')
