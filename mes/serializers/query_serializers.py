from rest_framework import serializers

class TimeSeriesRequestQuerySerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

class DetailFilterQuerySerializer(serializers.Serializer):
    from .model_serializers import StyleSerializer, LineSerializer
    style = StyleSerializer()
    line = LineSerializer()
    start_date_time = serializers.DateTimeField()
    end_date_time = serializers.DateTimeField()