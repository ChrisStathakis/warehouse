from rest_framework import serializers
from ..models import RetailOrder


class RetailOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = RetailOrder
        fields = '__all__'