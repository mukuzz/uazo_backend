from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'production-order', views.ProductionOrderViewSet)
router.register(r'style', views.StyleViewSet)
router.register(r'production-session', views.ProductionSessionViewSet)
router.register(r'qc-input', views.QcInputViewSet)
router.register(r'defect', views.DefectViewSet)
router.register(r'metric', views.Metric, basename="metric")

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls'))
]
