from .models import ProductionOrder, Style, ProductionSession, QcInput, Defect
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ProductionOrderSerializer, StyleSerializer, ProductionSessionSerializer, QcInputSerializer, DefectSerializer


class ProductionOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]


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
        production_sessions = ProductionSession.objects.all()
        if len(production_sessions) == 0:
            return Response({'error':'No sessions found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(production_sessions, many=True)
        return Response(serializer.data)


class QcInputViewSet(viewsets.ModelViewSet):
    queryset = QcInput.objects.all()
    serializer_class = QcInputSerializer
    permission_classes = [permissions.AllowAny]


class DefectViewSet(viewsets.ModelViewSet):
    queryset = Defect.objects.all()
    serializer_class = DefectSerializer
    permission_classes = [permissions.AllowAny]