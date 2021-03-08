from mes.models import ProductionOrder, Style, ProductionSession, QcInput, DeletedQcInput, Defect
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from mes.serializers.model_serializers import *
from mes.serializers.query_serializers import TimeSeriesRequestQuerySerializer, DetailFilterQuerySerializer
from django.utils import timezone
from datetime import timedelta
import datetime
from django.db.models import Sum, Count, Q, Value, CharField, F
from django.db.models.functions import Coalesce, Concat, Cast
import math
from . import utils
import os

@api_view(['GET'])
def get_user(request):
    user = request.user
    return Response({
        'id': user.id,
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

class LineViewSet(viewsets.ModelViewSet):
    queryset = Line.objects.all()
    serializer_class = LineSerializer


class Metric(viewsets.ViewSet):

    @action(detail=False, url_path="orders-progress")
    def orders_progress(self, request):
        start_time, end_time, order_id, style_id, line_id, affectMetricsByTime = utils.get_filter_values_from_query_params(request.query_params)

        orders_filter = ProductionOrder.objects.filter(due_date_time__gte=start_time)
        if order_id != None:
            orders_filter = orders_filter.filter(id=order_id)
        data = []
        for order in orders_filter:
            produced = 0
            if affectMetricsByTime:
                qc_inputs = utils.get_filtered_qc_inputs(start_time, end_time, order.id, style_id, line_id)
            else:
                qc_inputs = utils.get_filtered_qc_inputs(None, None, order.id, style_id, line_id)
            qc_inputs = qc_inputs.filter(Q(input_type=QcInput.FTT) | Q(input_type=QcInput.RECTIFIED))
            for qc_input in qc_inputs:
                produced += qc_input.quantity
            if affectMetricsByTime:
                target = utils.get_production_target_for_order(order, start_time, end_time, style_id, line_id)
            else:
                target = order.quantity()
            data.append({"label": order.buyer.buyer, "produced": produced, "target": target})
        return Response({"data": data})
    
    @action(detail=False, url_path="styles-progress")
    def styles_progress(self, request):
        start_time, end_time, order_id, style_id, line_id, affectMetricsByTime = utils.get_filter_values_from_query_params(request.query_params)

        styles_filter = Style.objects.filter(order__due_date_time__gte=start_time)
        if style_id != None:
            styles_filter = styles_filter.filter(id=style_id)
        if order_id != None:
            styles_filter = styles_filter.filter(order__id=order_id)
        data = []
        for style in styles_filter:
            produced = 0
            if affectMetricsByTime:
                qc_inputs = utils.get_filtered_qc_inputs(start_time, end_time, order_id, style.id, line_id)
            else:
                qc_inputs = utils.get_filtered_qc_inputs(None, None, order_id, style.id, line_id)
            qc_inputs = qc_inputs.filter(Q(input_type=QcInput.FTT) | Q(input_type=QcInput.RECTIFIED))
            for qc_input in qc_inputs:
                produced += qc_input.quantity
            if affectMetricsByTime:
                target = utils.get_production_target_for_style(style, start_time, end_time, order_id, line_id)
            else:
                target = style.quantity()
            data.append({
                "label": f'{style.number}',
                "produced": produced,
                "target": target,
            })
        return Response({"data": data})
    
    @action(detail=False, url_path="lines-progress")
    def lines_progress(self, request):
        start_time, end_time, order_id, style_id, line_id, _ = utils.get_filter_values_from_query_params(request.query_params)
        prod_sessions = utils.get_filtered_prod_sessions(start_time, end_time, order_id, style_id, line_id)

        unique_active_lines = set()
        targets = {}
        productions = {}
        for session in prod_sessions:
            unique_active_lines.add(session.line)
            try:
                targets[session.line.number] += session.target
            except KeyError:
                targets[session.line.number] = session.target
            produced = 0
            qc_inputs = utils.get_filtered_qc_inputs(start_time, end_time, order_id, style_id, line_id)
            qc_inputs = qc_inputs.filter(production_session=session)\
                .filter(Q(input_type=QcInput.FTT) | Q(input_type=QcInput.RECTIFIED))
            for qc_input in qc_inputs:
                produced += qc_input.quantity
            try:
                productions[session.line.number] += produced
            except KeyError:
                productions[session.line.number] = produced
        active_lines = list(unique_active_lines)
        data = []
        for line in active_lines:
            data.append({
                "label": f'Line {line.number}',
                "produced": productions[line.number],
                "target": targets[line.number],
            })
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
        _, prod_start_time, _, _, _ = utils.get_prod_sessions_and_timings(start)

        if end - start > timedelta(days=90):
            raise serializers.ValidationError({"date range should be less than or equal to 90 days"})

        labels, data = [], []
        output = 0

        qc_inputs = QcInput.objects\
            .filter(datetime__lte=prod_start_time)\
            .filter(Q(input_type=QcInput.FTT) | Q(input_type=QcInput.RECTIFIED))
        for qc_input in qc_inputs:
            output += qc_input.quantity
        if output > 0:
            labels.append(timezone.localtime(prod_start_time))
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

    @action(detail=False, url_path="efficiency")
    def efficiency(self, request):
        start_time, end_time, order_id, style_id, line_id, _ = utils.get_filter_values_from_query_params(request.query_params)
        prod_sessions = utils.get_filtered_prod_sessions(start_time, end_time, order_id, style_id, line_id)

        filter_date_time = end_time
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

    @action(detail=False, url_path="qc-actions")
    def qc_actions(self, request):
        start_time, end_time, order_id, style_id, line_id, _ = utils.get_filter_values_from_query_params(request.query_params)
        prod_sessions = utils.get_filtered_prod_sessions(start_time, end_time, order_id, style_id, line_id)
        
        resp = {
            "ftt": 0, "defective": 0, "rectified": 0, "rejected": 0, "ftt_percentage": "0.00%",
            "defective_percentage": "0.00%", "rectified_percentage": "0.00%", "rejected_percentage": "0.00%",
        }

        stats = utils.get_stats(prod_sessions, start_time, end_time)
        if stats != None:
            for key in resp.keys():
                try:
                    resp[key] = stats[key]
                except KeyError:
                    pass
        return Response(resp)
    
    @action(detail=False, url_path="key-stats")
    def key_stats(self, request):
        start_time, end_time, order_id, style_id, line_id, _ = utils.get_filter_values_from_query_params(request.query_params)

        headings = [
            "line", "buyer", "style", "target", "production", "rtt", "rtt_variance",
            "projected", "dhu", "efficiency",
            # "defective", "rectified" ,"rejected",
            "operators", "helpers", "shift"
        ]
        table_data = []

        prod_sessions = utils.get_filtered_prod_sessions(start_time, end_time, order_id, style_id, line_id)

        for prod_session in prod_sessions:
            session_key_stats = utils.get_stats([prod_session], start_time, end_time)
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
        start_time, end_time, order_id, style_id, line_id, _ = utils.get_filter_values_from_query_params(request.query_params)

        headings = [
            "hour", "production", "target", "target_variance", "dhu",
            "efficiency", "target_efficiency", "ftt_percentage", "defective_percentage"
        ]
        table_data = []

        prod_sessions, prod_start_time, prod_duration, break_start_time, break_duration = utils.get_prod_sessions_and_timings(end_time)
        prod_sessions = utils.apply_filters_on_prod_sessions(prod_sessions, order_id, style_id, line_id)

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
        start_time, end_time, order_id, style_id, line_id, _ = utils.get_filter_values_from_query_params(request.query_params)

        prod_sessions, prod_start_time, prod_duration, break_start_time, break_duration = utils.get_prod_sessions_and_timings(end_time)
        prod_sessions = utils.apply_filters_on_prod_sessions(prod_sessions, order_id, style_id, line_id)
        
        headings = [""]
        table_data = []

        if line_id is not None:
            lines = Line.objects.filter(id=line_id)
        else:
            lines = Line.objects.all()
        lines = lines.order_by('number')
            
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
        start_time, end_time, order_id, style_id, line_id, _ = utils.get_filter_values_from_query_params(request.query_params)

        qc_inputs = utils.get_filtered_qc_inputs(start_time, end_time, order_id, style_id, line_id)
        qc_inputs = qc_inputs.filter(input_type=QcInput.DEFECTIVE)
        qc_inputs = qc_inputs.annotate(affected_line=F('production_session__line__number'))

        defects_data = {}
        for qc_input in qc_inputs:
            for defect in qc_input.defects.all():
                try:
                    d_data = defects_data[defect.id]
                    # Add data if defect already added to dict
                    d_data["freq"] += qc_input.quantity
                    d_data["affected_lines"].add(str(qc_input.affected_line)),
                except KeyError:
                    defects_data[defect.id] = {
                        "id": defect.id,
                        "operation": defect.operation,
                        "defect": defect.defect,
                        "freq": qc_input.quantity,
                        "affected_lines": set([str(qc_input.affected_line)]),
                    }
                    
        defects_data_list = []
        for key, value in defects_data.items():
            value["affected_lines"] = ", ".join(list(value["affected_lines"]))
            defects_data_list.append(value)
        sorted_defects_data_list = sorted(defects_data_list, key=lambda x: x["freq"], reverse=True)
        return Response({"data": sorted_defects_data_list[:5]})