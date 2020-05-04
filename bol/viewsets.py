from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from bol.models import Client, Shipment
from bol.serializers import ClientSerializer, ShipmentSerializer
from bol.tasks import TaskGetShipmentData


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.filter()
    serializer_class = ClientSerializer

    @action(methods=['get'], detail=True)
    def shipment(self, request, pk):
        queryset = Shipment.objects.filter(client_id__exact=pk)
        serializer = ShipmentSerializer(queryset, many=True)
        if queryset.count() > 0:
            return Response(data=serializer.data)
        else:
            return Response({})

    @action(methods=['get'], detail=True)
    def initial_sync(self, request, pk):
        task = TaskGetShipmentData()
        task.delay(1, pk)
        return Response({'status': 'Initial Data Sync Started'})



class ShipmentViewset(ReadOnlyModelViewSet):
    queryset = Shipment.objects.filter()
    serializer_class = ShipmentSerializer
