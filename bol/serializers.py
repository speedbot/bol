from rest_framework.serializers import ModelSerializer

from bol.models import Client, Customer, Shipment, ShipmentItem, Transport


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'client_id', 'client_secret', 'expiry_date')


class TransportSerializer(ModelSerializer):
    class Meta:
        model = Transport
        fields = ('id', 'transportId', 'transporterCode', 'trackAndTrace')


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'salutationCode', 'zipCode', 'countryCode')


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
        )


class ShipmentSerializer(ModelSerializer):
    transport = TransportSerializer()
    customerDetails = CustomerSerializer()
    shipmentItems = ShipmentItemSerializer(many=True)

    class Meta:
        model = Shipment
        fields = (
            'shipmentId',
            'shipmentDate',
            'pickUpPoint',
            'shipmentItems',
            'transport',
            'customerDetails',
        )
