#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        # print ">>>>>>", username, password
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                return Response({'status':200, 'data': "Success!"})
            else:
                return Response({'status':500, 'data': "The password is valid, but the account has been disabled!"})

        else:
            return Response({'status':500, 'data': 'The username and password were incorrect.'})

class LogoutView(APIView):
    def get(self, request, *args, **kwargs):
        logout(request)  # 退出登录
        return Response({'status':200, 'data': 'logout'})

class CurrentUser(APIView):
    def get(self, request, *args, **kwargs):
        authority = False
        user = request.user.username
        if user in ('aili', 'wutao', 'jiangyun'):
            authority = True
        return Response({'status':200, 'data': authority})
