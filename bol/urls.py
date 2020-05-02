
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from bol.viewsets import ClientViewSet, ShipmentViewset

router = DefaultRouter()
router.register(r'client', ClientViewSet)
router.register(r'shipment', ShipmentViewset)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
]
