from mes.models import ProductionOrder, Style, ProductionSession, QcInput, DeletedQcInput, Defect
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from mes.serializers.model_serializers import *
from mes.serializers.query_serializers import TimeSeriesRequestQuerySerializer, DetailFilterQuerySerializer
from django.utils import timezone
from datetime import timedelta
import datetime
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMinute, TruncHour, TruncHour, TruncDate, TruncMonth
import math
from . import utils

# DAY_START_HOUR = 8
# DAY_WORK_HOURS = 8
# BREAK_START_HOUR = 13
# BREAK_START_MINUTE = 30
# BREAK_MINUTES = 30

DAY_START_HOUR = 0
DAY_WORK_HOURS = 8
BREAK_START_HOUR = 5
BREAK_START_MINUTE = 30
BREAK_MINUTES = 30

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
        defects = Defect.objects.annotate(defect_freq=Sum('qcinput__quantity')).order_by('-defect_freq')[:5]
        data = []
        for defect in defects[:5]:
            if defect.defect_freq != None:
                if defect.defect_freq > 0:
                    data.append({
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
        current_time = timezone.now()
        active_production_sessions = ProductionSession.get_active()
        manpower, elapsed_seconds, duration_seconds, sam, output, target = 0, 0, 0, 0, 0, 0
        for production_session in active_production_sessions:
            manpower += production_session.operators + production_session.helpers
            elapsed_seconds += (current_time - production_session.start_time).total_seconds()
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
        active_production_sessions = ProductionSession.get_active()
        ftt, defective, rejected, rectified = 0, 0, 0, 0
        for prod_session in active_production_sessions:
            qc_inputs = prod_session.qcinput_set.filter()
            for qc_input in qc_inputs:
                if qc_input.input_type == QcInput.FTT:
                    ftt += qc_input.quantity
                elif qc_input.input_type == QcInput.DEFECTIVE:
                    defective += qc_input.quantity
                elif qc_input.input_type == QcInput.REJECTED:
                    rejected += qc_input.quantity
                elif qc_input.input_type == QcInput.RECTIFIED:
                    rectified += qc_input.quantity
        return Response({"ftt": ftt, "defective": defective, "rectified": rectified, "rejected": rejected})
    
    @action(detail=False, url_path="key-stats")
    def key_stats(self, request):
        active_sessions = ProductionSession.get_active()

        headings = [
            "line", "buyer", "style", "target", "production", "rtt", "rtt_variance",
            "projected", "dhu", "efficiency",
            # "defective", "rectified" ,"rejected",
            "operators", "helpers", "shift"
        ]
        table_data = []

        for prod_session in active_sessions:
            session_key_stats = utils.get_stats([prod_session], prod_session.start_time, prod_session.end_time)
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
        headings = [
            "hour", "production", "target", "target_variance", "rtt", "rtt_variance", "dhu",
            "efficiency", "target_efficiency", "target_efficiency_variance", "ftt_rate", "defective_rate"
        ]
        table_data = []
        # production_sessions = ProductionSession.get_active()

        # Multi day production sessions will not be selected with this method
        current_time = timezone.localtime(timezone.now())
        day_start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end_time = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)
        production_start_date_time = current_time.replace(hour=DAY_START_HOUR, minute=0, second=0, microsecond=0)
        break_start_date_time = current_time.replace(hour=BREAK_START_HOUR, minute=BREAK_START_MINUTE, second=0, microsecond=0)
        break_duration = timedelta(minutes=BREAK_MINUTES)
        production_sessions = ProductionSession.objects.filter(
            start_time__gte=day_start_time,
            end_time__lte=day_end_time,
        )

        for hour in range(DAY_WORK_HOURS):
            time_filter_start = production_start_date_time + timedelta(hours=1*hour)
            time_filter_end = time_filter_start + timedelta(hours=1)
            if time_filter_end > break_start_date_time:
                time_filter_start += break_duration
                time_filter_end += break_duration
            stats = utils.get_stats(production_sessions, time_filter_start, time_filter_end)
            if stats != None:
                table_row = [f'{time_filter_start.strftime("%I:%M %p")} - {time_filter_end.strftime("%I:%M %p")}']
                for heading in headings[1:]:
                    try:
                        table_row.append(stats[heading])
                    except KeyError:
                        table_row.append('-')
                table_data.append(table_row)
        
        return Response({"headings": headings,"tableData":table_data})

    @action(detail=False, url_path="hourly-production")
    def hourly_production(self, request, pk=None):
        headings = [""]
        table_data = []

        lines = Line.objects.all().order_by('number')

        # Multi day production sessions will not be selected with this method
        current_time = timezone.localtime(timezone.now())
        day_start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end_time = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)
        production_start_date_time = current_time.replace(hour=DAY_START_HOUR, minute=0, second=0, microsecond=0)
        break_start_date_time = current_time.replace(hour=BREAK_START_HOUR, minute=BREAK_START_MINUTE, second=0, microsecond=0)
        break_duration = timedelta(minutes=BREAK_MINUTES)

        headings += [f'Line {line.number}' for line in lines]
        for hour in range(DAY_WORK_HOURS):
            time_filter_start = production_start_date_time + timedelta(hours=1*hour)
            time_filter_end = time_filter_start + timedelta(hours=1)
            if time_filter_end > break_start_date_time:
                time_filter_start += break_duration
                time_filter_end += break_duration
            table_row = [f'{time_filter_start.strftime("%I:%M %p")} - {time_filter_end.strftime("%I:%M %p")}']
            for line in lines:
                production_sessions = ProductionSession.objects.filter(
                    start_time__gte=day_start_time,
                    end_time__lte=day_end_time,
                    line=line
                )
                stats = utils.get_stats(production_sessions, time_filter_start, time_filter_end)
                if stats != None:
                    try:
                        table_row.append(stats['production'])
                    except KeyError:
                        table_row.append('-')
            table_data.append(table_row)
        
        return Response({"headings": headings,"tableData":table_data})