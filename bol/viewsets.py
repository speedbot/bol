from rest_framework.viewsets import  ModelViewSet

from bol.models import Client, ShipmentItem , Transport , Customer ,Shipment
from bol.serializers import ClientSerializer, TransportSerializer, CustomerSerializer, ShipmentItemSerializer, ShipmentSerializer


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.filter()
    serializer_class = ClientSerializer


class TransportViewSet(ModelViewSet):
    queryset = Transport.objects.filter()
    serializer_class = TransportSerializer


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.filter()
    serializer_class = CustomerSerializer


class ShipmentItemViewSet(ModelViewSet):
    queryset = ShipmentItem.objects.filter()
    serializer_class = ShipmentItemSerializer


class ShipmentViewset(ModelViewSet):
    queryset = Shipment.objects.filter()
    serializer_class = ShipmentSerializer
