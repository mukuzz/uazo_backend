from rest_framework import serializers
from .models import ProductionOrder, Style, ProductionSession, QcInput

class ProductionOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionOrder
        fields = '__all__'


class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
        fields = '__all__'


class ProductionSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionSession
        fields = '__all__'


class QcInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = QcInput
        fields = '__all__'


