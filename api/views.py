from .models import ProductionOrder, Style, ProductionSession, QcInput
from rest_framework import viewsets, permissions
from .serializers import ProductionOrderSerializer, StyleSerializer, ProductionSessionSerializer, QcInputSerializer


class ProductionOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class StyleViewSet(viewsets.ModelViewSet):
    queryset = Style.objects.all()
    serializer_class = StyleSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductionSessionViewSet(viewsets.ModelViewSet):
    queryset = ProductionSession.objects.all()
    serializer_class = ProductionSessionSerializer
    permission_classes = [permissions.IsAuthenticated]


class QcInputViewSet(viewsets.ModelViewSet):
    queryset = QcInput.objects.all()
    serializer_class = QcInputSerializer
    permission_classes = [permissions.IsAuthenticated]