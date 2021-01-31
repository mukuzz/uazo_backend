from django.urls import path, include
from rest_framework import routers
from .views import ProductionOrderViewSet, StyleViewSet, ProductionSessionViewSet, QcInputViewSet, DefectViewSet, ProductionLine

router = routers.DefaultRouter()
router.register(r'production-order', ProductionOrderViewSet)
router.register(r'style', StyleViewSet)
router.register(r'production-session', ProductionSessionViewSet)
router.register(r'qc-input', QcInputViewSet)
router.register(r'defect', DefectViewSet)
router.register(r'production-line', ProductionLine, basename="ProductionLine")

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls'))
]
