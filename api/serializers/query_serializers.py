from rest_framework import serializers

class TimeSeriesRequestQuerySerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()