from django.urls import path, include
from rest_framework import routers
from .views import ProductionOrderViewSet, StyleViewSet, ProductionSessionViewSet, QcInputViewSet

router = routers.DefaultRouter()
router.register(r'production-order', ProductionOrderViewSet)
router.register(r'style', StyleViewSet)
router.register(r'production-session', ProductionSessionViewSet)
router.register(r'qc-input', QcInputViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls'))
]
