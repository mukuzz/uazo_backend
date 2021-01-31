from .models import ProductionOrder, Style, ProductionSession, QcInput, Defect
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ProductionOrderSerializer, StyleSerializer, ProductionSessionSerializer, QcInputSerializer, DefectSerializer
from django.utils import timezone
import math

class ProductionOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    @action(detail=False)
    def active(self, request):
        active_orders = ProductionOrder.objects.filter(completed=False)
        if len(active_orders) == 0:
            return Response({'error':'No active orders found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(active_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, url_path='active-volume')
    def active_volume(self, request):
        active_orders = ProductionOrder.objects.filter(completed=False)
        active_volume = 0
        for order in active_orders:
            active_volume += order.quantity
        return Response({"data": active_volume})

    @action(detail=False, url_path='active-progress')
    def active_progress(self, request):
        active_orders = ProductionOrder.objects.filter(completed=False)
        produced = 0
        for order in active_orders:
            qc_inputs = QcInput.objects.filter(production_session__style__order=order)
            for qc_input in qc_inputs:
                if qc_input.input_type == "ftt" or qc_input.input_type == "rectified":
                    produced += qc_input.quantity
        return Response({"data": produced})
    
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
    permission_classes = [permissions.AllowAny]


class ProductionSessionViewSet(viewsets.ModelViewSet):
    queryset = ProductionSession.objects.all()
    serializer_class = ProductionSessionSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False)
    def active(self, request):
        active_production_sessions = ProductionSession.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        )
        if len(active_production_sessions) == 0:
            return Response({'error':'No active sessions found'}, status=status.HTTP_404_NOT_FOUND)
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

        for qc_input in production_session.qcinput_set.all():
            if qc_input.redacted:
                continue
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

        output = ftt + rectified
        stats = {
            "output": output,   
            "buyer": style.order.buyer,
            "style_number": style.number,
            "style_name": style.name,
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
            shift_seconds_elapsed = (timezone.now() - shift_start).total_seconds()
            shift_seconds_remaining = (shift_end - timezone.now()).total_seconds()
            rtt = output + (output / shift_seconds_elapsed) * shift_seconds_remaining
            stats["rtt"] = rtt

            # Calculate Variance
            squared_difference = pow(production_session.target,2) - pow(rtt,2)
            if squared_difference > 0:
                stats["variance"] = math.sqrt(squared_difference)

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
    permission_classes = [permissions.AllowAny]


class DefectViewSet(viewsets.ModelViewSet):
    queryset = Defect.objects.all()
    serializer_class = DefectSerializer
    permission_classes = [permissions.AllowAny]


class ProductionLine(viewsets.ViewSet):
    permission_classes = []

    @action(detail=False)
    def active(self, request):
        active_production_sessions = ProductionSession.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        )
        active_lines = set()
        for session in active_production_sessions:
            active_lines.add(session.line_number)
        return Response({"data": len(active_lines)})