from rest_framework import serializers
from django.utils import timezone

class TimeSeriesRequestQuerySerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

class DetailFilterQuerySerializer(serializers.Serializer):
    filterDateTime = serializers.DateTimeField(default=timezone.now)
    # filterStyle = serializers.PrimaryKeyRelatedField()