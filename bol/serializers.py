from rest_framework.serializers import ModelSerializer

from bol.models import Client, Customer, Shipment, ShipmentItem, Transport


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'client_id', 'client_secret')


class TransportSerializer(ModelSerializer):
    class Meta:
        model = Transport
        fields = ('id', 'transportId', 'transporterCode', 'trackAndTrace')


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'email', 'salutationCode', 'zipCode', 'countryCode')


class ShipmentItemSerializer(ModelSerializer):
    class Meta:
        model = ShipmentItem
        fields = (
            'id',
            'orderItemId',
            'orderId',
            'orderDate',
            'latestDeliveryDate',
            'ean',
            'title',
            'quantity',
            'offerPrice',
            'offerCondition',
            'fulfilmentMethod',
            'offerReference',
        )


class ShipmentSerializer(ModelSerializer):
    transport = TransportSerializer()
    customerDetails = CustomerSerializer()
    shipmentItems = ShipmentItemSerializer(many=True)

    class Meta:
        model = Shipment
        fields = (
            'id',
            'shipmentId',
            'shipmentDate',
            'pickUpPoint',
            'shipmentItems',
            'transport',
            'customerDetails',
            'shipmentReference',
        )
