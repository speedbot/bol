import logging
from bol.models import Shipment, ShipmentItem,Transport,Customer

def get_task_logger():
    return logging.getLogger('task_exceptions')


def tuple_instance(instance):
    return (instance._meta.app_label, instance._meta.model_name, instance.id)


def clean_db():
    models = [ShipmentItem, Transport, Customer, Shipment]
    for model in models:
        for item in model.objects.filter():
            item.delete()