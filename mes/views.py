from mes.models import ProductionOrder, Style, ProductionSession, QcInput, DeletedQcInput, Defect
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from mes.serializers.model_serializers import *
from mes.serializers.query_serializers import TimeSeriesRequestQuerySerializer
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMinute, TruncHour, TruncHour, TruncDate, TruncMonth
import math
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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
        order = self.get_object()
        qc_inputs = QcInput.objects.filter(production_session__style__order=order)
        produced = 0
        for qc_input in qc_inputs:
            if qc_input.input_type == "ftt" or qc_input.input_type == "rectified":
                produced += qc_input.quantity
        status = {"produced": produced}
        return Response(status)


class StyleViewSet(viewsets.ModelViewSet):
    queryset = Style.objects.all()
    serializer_class = StyleSerializer


class ProductionSessionViewSet(viewsets.ModelViewSet):
    queryset = ProductionSession.objects.all()
    serializer_class = ProductionSessionSerializer
    
    @action(detail=False)
    def active(self, request):
        active_production_sessions = ProductionSession.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        )
        serializer = self.get_serializer(active_production_sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def stats(self, request, pk=None):
        production_session = self.get_object()
        style = production_session.style
        ftt, defective, rejected, rectified, defects = 0, 0, 0, 0, 0

        # To avoid double counting while calculating total_pieces_processed
        # Rectified should always be ignored.
        # Rejected should be ignored if the piece came back after being marked defective.
        total_pieces_processed = 0

        qc_inputs = production_session.qcinput_set.filter()
        for qc_input in qc_inputs:
            if qc_input.input_type == "ftt":
                ftt += qc_input.quantity
            elif qc_input.input_type == "defective":
                defective += qc_input.quantity
                defects += len(qc_input.defects.all()) 
            elif qc_input.input_type == "rejected":
                rejected += qc_input.quantity
                if qc_input.ftt:
                    total_pieces_processed += qc_input.quantity
            elif qc_input.input_type == "rectified":
                rectified += qc_input.quantity
        
        total_pieces_processed += ftt + defective

        target = production_session.target
        output = ftt + rectified
        stats = {
            "target": target,
            "output": output,   
            "buyer": style.order.buyer,
            "style_number": style.number,
            "style_name": style.name,
            "defective": defective,
            "rejected": rejected,
            "rectified": rectified,
        }
        
        shift_start = production_session.start_time
        shift_end = production_session.end_time
        stats["shift"] = f'{timezone.localtime(shift_start).hour} to {timezone.localtime(shift_end).hour}'

        if output > 0 and timezone.now() >= shift_start and timezone.now() <= shift_end:
            # Calculate Line efficiency
            manpower = production_session.operators + production_session.helpers
            shift_mins_elapsed = (timezone.now() - shift_start).total_seconds() / 60
            stats["line_efficiency"] = output * style.sam * 100 / (manpower * shift_mins_elapsed)
        
            # Calculate RTT
            shift_duration_seconds = (shift_end - shift_start).total_seconds()
            shift_elapsed_seconds = (timezone.now() - shift_start).total_seconds()
            rtt = target * (shift_elapsed_seconds / shift_duration_seconds)
            stats["rtt"] = math.ceil(rtt)

            # Calculate Variance
            stats["variance"] = math.ceil(target - rtt)

            # Calculate Projected Output
            production_rate = output / shift_elapsed_seconds
            shift_remaining_seconds = (shift_end - timezone.now()).total_seconds()
            stats["projected_output"] = round(output + production_rate * shift_remaining_seconds)

        if ftt != 0:
            stats["ftt_rate"] = ftt * 100 / total_pieces_processed
        if rejected != 0:
            stats["reject_rate"] = rejected * 100 / total_pieces_processed
        if ftt != 0:
            stats["defective_rate"] = defective * 100 / total_pieces_processed
        if ftt != 0:
            stats["dhu"] = defects * 100 / total_pieces_processed
        return Response(stats)


class QcInputViewSet(viewsets.ModelViewSet):
    queryset = QcInput.objects.all()
    serializer_class = QcInputSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.send_channels_message()
    
    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.send_channels_message()
    
    def send_channels_message(self):
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            "sse_group",
            {
                "type": "send_new_qcinput_update"
            }
        )


class DefectViewSet(viewsets.ModelViewSet):
    queryset = Defect.objects.all()
    serializer_class = DefectSerializer

    @action(detail=False, url_path="most-frequent")
    def most_frequent(self, request):
        defects = Defect.objects.annotate(Sum('qcinput__quantity')).order_by('-qcinput__quantity__sum')
        data = []
        for defect in defects[:5]:
            if defect.qcinput__quantity__sum != None:
                if defect.qcinput__quantity__sum > 0:
                    data.append({
                        "operation": defect.operation,
                        "defect": defect.defect,
                        "count": defect.qcinput__quantity__sum
                    })
        return Response({"data": data})


class Metric(viewsets.ViewSet):

    # This exists just for the metric viewset to show up in the browsable mes
    def list(self, request):
        return Response()

    @action(detail=False, url_path="active-orders")
    def active_orders(self, request):
        active_orders = ProductionOrder.objects.filter(completed=False)
        data = []
        for order in active_orders:
            produced = 0
            qc_inputs = QcInput.objects.filter(production_session__style__order=order)
            for qc_input in qc_inputs:
                if qc_input.input_type == "ftt" or qc_input.input_type == "rectified":
                    produced += qc_input.quantity
            data.append({"buyer": order.buyer, "produced": produced, "target": order.quantity()})
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
        
        qc_inputs = QcInput.objects.filter(
            datetime__gte=start,
            datetime__lte=end,
        ).order_by('datetime')

        labels, data = [], []
        output = 0
        for qc_input in qc_inputs:
            output += qc_input.quantity
            labels.append(timezone.localtime(qc_input.datetime))
            data.append(output)
        return Response({"labels":labels, "data": data})

    
    @action(detail=False, url_path="active-lines")
    def active_lines(self, request):
        active_production_sessions = ProductionSession.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        )
        active_lines = set()
        for session in active_production_sessions:
            active_lines.add(session.line)
        return Response({"data": len(active_lines)})

    @action(detail=False, url_path="factory-efficiency")
    def factory_efficiency(self, request):
        current_time = timezone.now()
        active_production_sessions = ProductionSession.objects.filter(
            start_time__lte=current_time,
            end_time__gte=current_time
        )
        manpower, elapsed_seconds, duration_seconds, sam, output, target = 0, 0, 0, 0, 0, 0
        for production_session in active_production_sessions:
            manpower += production_session.operators + production_session.helpers
            elapsed_seconds += (current_time - production_session.start_time).total_seconds()
            duration_seconds = (production_session.end_time - production_session.start_time).total_seconds()
            res = production_session.qcinput_set \
                .filter(Q(input_type="ftt") | Q(input_type="rectified")) \
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
        active_production_sessions = ProductionSession.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        )
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
        active_production_sessions = ProductionSession.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        )
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
        active_production_sessions = ProductionSession.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        )
        ftt, defective, rejected, rectified = 0, 0, 0, 0
        for prod_session in active_production_sessions:
            qc_inputs = prod_session.qcinput_set.filter()
            for qc_input in qc_inputs:
                if qc_input.input_type == "ftt":
                    ftt += qc_input.quantity
                elif qc_input.input_type == "defective":
                    defective += qc_input.quantity
                elif qc_input.input_type == "rejected":
                    rejected += qc_input.quantity
                elif qc_input.input_type == "rectified":
                    rectified += qc_input.quantity
        return Response({"ftt": ftt, "defective": defective, "rectified": rectified, "rejected": rejected})
