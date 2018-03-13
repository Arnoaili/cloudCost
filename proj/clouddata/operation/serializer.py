# coding: utf-8
from rest_framework import serializers
from models import *


class FluxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flux
        fields = "__all__"

class PlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plat
        fields = "__all__"

class AwsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwsCost
        fields = "__all__"

class BigDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BigData
        fields = "__all__"

class OtherPlatCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherPlatCost
        fields = "__all__"

class QcloudOtherCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherCost
        fields = "__all__"

class ChinaPerMonthCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChinaPerMonthCost
        fields = "__all__"

class OverseasPerMonthCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = OverseasPerMonthCost
        fields = "__all__"

class QcloudCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = QcloudCost
        fields = "__all__"

class AliCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AliCost
        fields = "__all__"

class ZhaoWeiCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZhaoWeiCost
        fields = "__all__"

class LuGuCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LuGuCost
        fields = "__all__"

class UcloudCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = UcloudCost
        fields = "__all__"

class AwsCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwsShareCost
        fields = "__all__"
