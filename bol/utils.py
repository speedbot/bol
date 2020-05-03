import logging

from bol.models import Customer, Shipment, ShipmentItem, Transport


def get_task_logger():
    return logging.getLogger('task_exceptions')


# util method to clean db for testing purpose
def clean_db():
    models = [ShipmentItem, Transport, Customer, Shipment]
    for model in models:
        for item in model.objects.filter():
            item.delete()


# util method to get access to an API handler instance to access BOL API
def get_api_handler():
    from bol.models import Client
    from bol.handler import APIHandler
    return APIHandler(Client.objects.first())
