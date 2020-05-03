from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action

from bol.models import Client, Customer, Shipment, ShipmentItem, Transport
from bol.serializers import (ClientSerializer, CustomerSerializer,
                             ShipmentItemSerializer, ShipmentSerializer,
                             TransportSerializer)
from bol.tasks import TaskGetAllShipments


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.filter()
    serializer_class = ClientSerializer


class ShipmentViewset(ReadOnlyModelViewSet):
    queryset = Shipment.objects.filter()
    serializer_class = ShipmentSerializer

    @action(methods=['get'], detail=False)
    def initial_sync(self, request, pk=None):
        task = TaskGetAllShipments()
        task.delay()
        return Response({'status': 'Initial Data Sync Started'})
