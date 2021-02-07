from rest_framework import serializers

from .model_serializers import QcInputSerializer

class ManyQcInputSerializer(serializers.Serializer):
    qc_inputs = QcInputSerializer(many=True)