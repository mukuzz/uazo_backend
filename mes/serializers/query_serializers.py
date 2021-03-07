from rest_framework import serializers
from django.utils import timezone
from mes.models import Style
from .model_serializers import StyleSerializer

class TimeSeriesRequestQuerySerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

class DetailFilterQuerySerializer(serializers.Serializer):
    startDateTime = serializers.DateTimeField(default=timezone.now, required=False)
    endDateTime = serializers.DateTimeField(default=timezone.now, required=False)
    order = serializers.IntegerField(default=None, required=False)
    style = serializers.IntegerField(default=None, required=False)
    line = serializers.IntegerField(default=None, required=False)