from rest_framework import serializers
from .models import ProductionOrder, Style, ProductionSession, QcInput

class ProductionOrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProductionOrder
        fields = '__all__'


class StyleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Style
        fields = '__all__'


class ProductionSessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProductionSession
        fields = '__all__'


class QcInputSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = QcInput
        fields = '__all__'


