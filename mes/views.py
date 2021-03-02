from mes.models import ProductionOrder, Style, ProductionSession, QcInput, DeletedQcInput, Defect
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from mes.serializers.model_serializers import *
from mes.serializers.query_serializers import TimeSeriesRequestQuerySerializer, DetailFilterQuerySerializer
from django.utils import timezone
from datetime import timedelta
import datetime
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMinute, TruncHour, TruncHour, TruncDate, TruncMonth, Coalesce
import math
from . import utils
import os

DAY_START_HOUR = int(os.environ['DAY_START_HOUR'])
DAY_WORK_HOURS = int(os.environ['DAY_WORK_HOURS'])
BREAK_START_HOUR = int(os.environ['BREAK_START_HOUR'])
BREAK_START_MINUTE = int(os.environ['BREAK_START_MINUTE'])
BREAK_MINUTES = int(os.environ['BREAK_MINUTES'])

# DAY_START_HOUR = 0
# DAY_WORK_HOURS = 8
# BREAK_START_HOUR = 5
# BREAK_START_MINUTE = 30
# BREAK_MINUTES = 30

@api_view(['GET'])
def get_user(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
    })

class ProductionOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer

    @action(detail=False)
    def active(self, request):
        active_orders = ProductionOrder.active()
        serializer = self.get_serializer(active_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def progress(self, request, pk=None):
        return Response({"produced": self.get_object().order.progress()})


class StyleViewSet(viewsets.ModelViewSet):
    queryset = Style.objects.all()
    serializer_class = StyleSerializer


class ProductionSessionViewSet(viewsets.ModelViewSet):
    queryset = ProductionSession.objects.all()
    serializer_class = ProductionSessionSerializer
    
    @action(detail=False)
    def active(self, request):
        # TODO: Return Sessions only which the user is authorized to
        active_production_sessions = ProductionSession.get_active()
        serializer = self.get_serializer(active_production_sessions, many=True)
        return Response(serializer.data)


class QcInputViewSet(viewsets.ModelViewSet):
    queryset = QcInput.objects.all()
    serializer_class = QcInputSerializer


class DefectViewSet(viewsets.ModelViewSet):
    queryset = Defect.objects.all()
    serializer_class = DefectSerializer

    @action(detail=False, url_path="most-frequent")
    def most_frequent(self, request):
        defects = Defect.objects.annotate(defect_freq=Coalesce(Sum('qcinput__quantity'),0)).order_by('-defect_freq')[:5]
        data = []
        for defect in defects:
            if defect.defect_freq != None:
                if defect.defect_freq > 0:
                    data.append({
                        "id": defect.id,
                        "operation": defect.operation,
                        "defect": defect.defect,
                        "freq": defect.defect_freq
                    })
        return Response({"data": data})


class Metric(viewsets.ViewSet):

    @action(detail=False, url_path="active-orders-status")
    def active_orders_status(self, request):
        active_orders = ProductionOrder.objects.filter(completed=False)
        data = []
        for order in active_orders:
            produced = 0
            qc_inputs = QcInput.objects\
                .filter(production_session__style__order=order)\
                .filter(Q(input_type=QcInput.FTT) | Q(input_type=QcInput.RECTIFIED))
            for qc_input in qc_inputs:
                produced += qc_input.quantity
            data.append({"buyer": order.buyer.buyer, "produced": produced, "target": order.quantity()})
        return Response({"data": data})

    @action(detail=False, url_path="output-timeseries")
    def output_timeseries(self, request):
        """
        start -- starting time of timeseires
        end -- ending time of timeseires
        intervals -- number of x axis intervals
        """
        query_params = TimeSeriesRequestQuerySerializer(data=request.query_params)
        query_params.is_valid(raise_exception=True)
        start = query_params.validated_data['start']
        end = query_params.validated_data['end']

        if end - start > timedelta(days=90):
            raise serializers.ValidationError({"date range should be less than or equal to 90 days"})

        labels, data = [], []
        output = 0

        qc_inputs = QcInput.objects\
            .filter(datetime__lte=start)\
            .filter(Q(input_type=QcInput.FTT) | Q(input_type=QcInput.RECTIFIED))
        for qc_input in qc_inputs:
            output += qc_input.quantity
        if output > 0:
            labels.append(timezone.localtime(start))
            data.append(output)
        
        qc_inputs = QcInput.objects\
            .filter(datetime__gt=start,datetime__lte=end)\
            .filter(Q(input_type=QcInput.FTT) | Q(input_type=QcInput.RECTIFIED))\
            .order_by('datetime')

        for qc_input in qc_inputs:
            output += qc_input.quantity
            labels.append(timezone.localtime(qc_input.datetime))
            data.append(output)
        return Response({"labels":labels, "data": data})

    
    @action(detail=False, url_path="active-lines")
    def active_lines(self, request):
        active_production_sessions = ProductionSession.get_active()
        active_lines = set()
        for session in active_production_sessions:
            active_lines.add(session.line)
        return Response({"data": [LineSerializer(line).data for line in active_lines]})

    @action(detail=False, url_path="factory-efficiency")
    def factory_efficiency(self, request):
        query_params = DetailFilterQuerySerializer(data=request.query_params)
        query_params.is_valid(raise_exception=True)
        filter_date_time = query_params.validated_data['filterDateTime']

        prod_sessions, prod_start_time, prod_duration, _, _ = utils.get_prod_sessions_and_timings(filter_date_time)

        manpower, elapsed_seconds, duration_seconds, sam, output, target = 0, 0, 0, 0, 0, 0
        for production_session in prod_sessions:
            adjusted_filter_date_time = filter_date_time
            if filter_date_time < production_session.start_time:
                adjusted_filter_date_time = production_session.start_time
            elif filter_date_time > production_session.end_time:
                adjusted_filter_date_time = production_session.end_time
            manpower += production_session.operators + production_session.helpers
            elapsed_seconds += (adjusted_filter_date_time - production_session.start_time).total_seconds()
            duration_seconds = (production_session.end_time - production_session.start_time).total_seconds()
            res = production_session.qcinput_set \
                .filter(Q(input_type=QcInput.FTT) | Q(input_type=QcInput.RECTIFIED)) \
                .aggregate(Sum('quantity'))
            if res['quantity__sum'] != None:
                output += res['quantity__sum']
            sam += production_session.style.sam
            target += production_session.target
        
        required_efficiency, factory_efficiency = 0, 0
        try:
            factory_efficiency = output * sam * 100 / (manpower * elapsed_seconds / 60)
        except ZeroDivisionError:
            factory_efficiency = 0
        try:
            rtt = target * (elapsed_seconds / duration_seconds)
            required_efficiency = rtt * sam * 100 / (manpower * elapsed_seconds / 60)
        except ZeroDivisionError:
            required_efficiency = 0
        return Response({"target": required_efficiency, "actual": factory_efficiency})

    @action(detail=False, url_path="active-operators")
    def active_operators(self, request):
        active_production_sessions = ProductionSession.get_active()
        if len(active_production_sessions) == 0:
            return Response({"data": 0})
        operators_on_line = {}
        for session in active_production_sessions:
            try:
                operators_on_line[str(session.line)]
            except KeyError:
                operators_on_line[str(session.line)] = 0
            operators_on_line[str(session.line)] = \
                max(operators_on_line[str(session.line)], session.operators)
        operators = 0
        for _, value in operators_on_line.items():
            operators += value
        return Response({"data": operators})
        
    @action(detail=False, url_path="active-helpers")
    def active_helpers(self, request):
        active_production_sessions = ProductionSession.get_active()
        if len(active_production_sessions) == 0:
            return Response({"data": 0})
        helpers_on_line = {}
        for session in active_production_sessions:
            try:
                helpers_on_line[str(session.line)]
            except KeyError:
                helpers_on_line[str(session.line)] = 0
            helpers_on_line[str(session.line)] = \
                max(helpers_on_line[str(session.line)], session.helpers)
        helpers = 0
        for _, value in helpers_on_line.items():
            helpers += value
        return Response({"data": helpers})

    @action(detail=False, url_path="active-qc-actions")
    def active_qc_actions(self, request):
        query_params = DetailFilterQuerySerializer(data=request.query_params)
        query_params.is_valid(raise_exception=True)
        filter_date_time = query_params.validated_data['filterDateTime']
        
        resp = {
            "ftt": 0, "defective": 0, "rectified": 0, "rejected": 0, "ftt_percentage": "0.00%",
            "defective_percentage": "0.00%", "rectified_percentage": "0.00%", "rejected_percentage": "0.00%",
        }

        prod_sessions, _, _, _, _ = utils.get_prod_sessions_and_timings(filter_date_time)
        day_start_time = filter_date_time.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end_time = filter_date_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        stats = utils.get_stats(prod_sessions, day_start_time, day_end_time)
        if stats != None:
            for key in resp.keys():
                try:
                    resp[key] = stats[key]
                except KeyError:
                    pass
        return Response(resp)
    
    @action(detail=False, url_path="key-stats")
    def key_stats(self, request):
        query_params = DetailFilterQuerySerializer(data=request.query_params)
        query_params.is_valid(raise_exception=True)
        filter_date_time = query_params.validated_data['filterDateTime']

        headings = [
            "line", "buyer", "style", "target", "production", "rtt", "rtt_variance",
            "projected", "dhu", "efficiency",
            # "defective", "rectified" ,"rejected",
            "operators", "helpers", "shift"
        ]
        table_data = []

        prod_sessions, _, _, _, _ = utils.get_prod_sessions_and_timings(filter_date_time)
        day_start_time = filter_date_time.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end_time = filter_date_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        for prod_session in prod_sessions:
            session_key_stats = utils.get_stats([prod_session], day_start_time, day_end_time)
            table_row = []
            for heading in headings:
                try:
                    table_row.append(session_key_stats[heading])
                except KeyError:
                    table_row.append('-')
            table_data.append(table_row)
        return Response({"headings": headings, "tableData": table_data})
    
    @action(detail=False, url_path="hourly-stats")
    def hourly_stats(self, request, pk=None):
        query_params = DetailFilterQuerySerializer(data=request.query_params)
        query_params.is_valid(raise_exception=True)
        filter_date_time = query_params.validated_data['filterDateTime']

        headings = [
            "hour", "production", "target", "target_variance", "dhu",
            "efficiency", "target_efficiency", "target_efficiency_variance", "ftt_percentage", "defective_percentage"
        ]
        table_data = []

        prod_sessions, prod_start_time, prod_duration, break_start_time, break_duration = utils.get_prod_sessions_and_timings(filter_date_time)

        hour = 0
        while True:
            time_filter_start = prod_start_time + timedelta(hours=1*hour)
            time_filter_end = time_filter_start + timedelta(hours=1)
            if time_filter_end > break_start_time:
                time_filter_start += break_duration
                time_filter_end += break_duration
            stats = utils.get_stats(prod_sessions, time_filter_start, time_filter_end)
            if stats != None:
                table_row = [f'{time_filter_start.strftime("%I:%M %p")} - {time_filter_end.strftime("%I:%M %p")}']
                for heading in headings[1:]:
                    try:
                        table_row.append(stats[heading])
                    except KeyError:
                        table_row.append('-')
                table_data.append(table_row)
            
            hour += 1
            if time_filter_end >= prod_start_time + prod_duration:
                break
        
        return Response({"headings": headings,"tableData":table_data})

    @action(detail=False, url_path="hourly-production")
    def hourly_production(self, request, pk=None):
        query_params = DetailFilterQuerySerializer(data=request.query_params)
        query_params.is_valid(raise_exception=True)
        filter_date_time = query_params.validated_data['filterDateTime']

        headings = [""]
        table_data = []

        lines = Line.objects.all().order_by('number')

        prod_sessions, prod_start_time, prod_duration, break_start_time, break_duration = utils.get_prod_sessions_and_timings(filter_date_time)

        headings += [f'Line {line.number}' for line in lines]
        hour = 0
        while True:
            time_filter_start = prod_start_time + timedelta(hours=1*hour)
            time_filter_end = time_filter_start + timedelta(hours=1)
            if time_filter_end > break_start_time:
                time_filter_start += break_duration
                time_filter_end += break_duration
            table_row = [f'{time_filter_start.strftime("%I:%M %p")} - {time_filter_end.strftime("%I:%M %p")}']
            for line in lines:
                production_sessions = prod_sessions.filter(line=line)
                stats = utils.get_stats(production_sessions, time_filter_start, time_filter_end)
                if stats != None:
                    try:
                        table_row.append(stats['production'])
                    except KeyError:
                        table_row.append('-')
            table_data.append(table_row)

            hour += 1
            if time_filter_end >= prod_start_time + prod_duration:
                break
        
        return Response({"headings": headings,"tableData":table_data})

    @action(detail=False, url_path="frequent-defects")
    def frequent_defects(self, request):
        query_params = DetailFilterQuerySerializer(data=request.query_params)
        query_params.is_valid(raise_exception=True)
        filter_date_time = query_params.validated_data['filterDateTime']

        day_start_time = filter_date_time.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end_time = filter_date_time.replace(hour=23, minute=59, second=59, microsecond=999999)
        defects = Defect.objects\
            .filter(qcinput__datetime__gte=day_start_time,qcinput__datetime__lte=day_end_time)\
            .annotate(defect_freq=Coalesce(Sum('qcinput__quantity'),0)).order_by('-defect_freq')[:5]
        data = []
        for defect in defects:
            if defect.defect_freq > 0:
                data.append({
                    "id": defect.id,
                    "operation": defect.operation,
                    "defect": defect.defect,
                    "freq": defect.defect_freq
                })
        return Response({"data": data})