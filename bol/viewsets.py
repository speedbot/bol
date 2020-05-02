from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from bol.models import Client, Customer, Shipment, ShipmentItem, Transport
from bol.serializers import (ClientSerializer, CustomerSerializer,
                             ShipmentItemSerializer, ShipmentSerializer,
                             TransportSerializer)


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.filter()
    serializer_class = ClientSerializer


class TransportViewSet(ReadOnlyModelViewSet):
    queryset = Transport.objects.filter()
    serializer_class = TransportSerializer


class CustomerViewSet(ReadOnlyModelViewSet):
    queryset = Customer.objects.filter()
    serializer_class = CustomerSerializer


class ShipmentItemViewSet(ReadOnlyModelViewSet):
    queryset = ShipmentItem.objects.filter()
    serializer_class = ShipmentItemSerializer


class ShipmentViewset(ReadOnlyModelViewSet):
    queryset = Shipment.objects.filter()
    serializer_class = ShipmentSerializer
