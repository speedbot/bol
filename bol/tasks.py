import logging

from billiard.exceptions import SoftTimeLimitExceeded
from django.db import DatabaseError, OperationalError
from ratelimit import RateLimitException

from bol.utils import get_api_handler
from celery.task import Task as CeleryTask

from .models import Client
from .utils import get_task_logger

task_logger = get_task_logger()


class TaskBase(object):
    default_retry_delay = 30
    max_retries = 3
    retry_on_time_limit_exceeded = False

    def run(self, *args, **kwargs):
        try:
            return self._run(*args, **kwargs)
        except (OperationalError, DatabaseError) as exc:
            raise self.retry(exc=exc)
        except SoftTimeLimitExceeded as exc:
            if self.retry_on_time_limit_exceeded:
                raise self.retry(exc=exc)
            get_task_logger().error(
                'Task failure {}: {}'.format(exc.__class__.__name__, exc),
                exc_info=True,
                extra={'run_args': args, 'run_kwargs': kwargs},
            )

    def _run(self, *args, **kwargs):
        raise NotImplementedError('Must define _run method.')


class Task(TaskBase, CeleryTask):
    """
    Base task for tasks that hit up the database.
    """
    pass


# Task to get shipment info using the shipmentId param
class CreateShipmentData(Task):
    def _run(self, shipmentId, client_id, *args, **kwargs):
        from bol.models import Transport, Customer, Shipment, ShipmentItem
        try:
            data = get_api_handler().get_shipment(shipmentId)
        except RateLimitException:
            self.retry(countdown=60)
        if data is None:
            return
        kwargs = data
        if 'transport' in data:
            transport_data = data.pop('transport')
            if Transport.objects.filter(transportId=transport_data['transportId']):
                Transport.objects.filter(
                    transportId=transport_data['transportId'],
                ).update(**transport_data)
            else:
                transport = Transport.objects.create(**transport_data)
                kwargs['transport'] = transport
        if 'customerDetails' in data:
            customer = Customer.objects.create(**data.pop('customerDetails'))
            kwargs['customerDetails'] = customer
        shipmentitems = data.pop('shipmentItems')
        list = []
        for shipment in shipmentitems:
            list.append(ShipmentItem.objects.create(**shipment))
        if Shipment.objects.filter(shipmentId=kwargs['shipmentId']):
            Shipment.objects.filter(shipmentId=kwargs['shipmentId']).update(**kwargs)
        else:
            obj = Shipment.objects.create(**kwargs)
            obj.client = Client.objects.filter(id=client_id).first()
            obj.save()
            for item in list:
                obj.shipmentItems.add(item)



# Task to get shipment data and recursively call itself to fetch data of consequent pages
class TaskGetShipmentData(Task):
    def _run(self, page, client_id, *args, **kwargs):
        final_result = []
        methods = ['FBR', 'FBB']

        for fullfillment_method in methods:
            params = {
                'fulfilment-method': fullfillment_method,
                'page': page,
            }
            try:
                shipments = get_api_handler().get_shipment_data(params)
                if shipments:
                    for item in shipments['shipments']:
                        final_result.append(item)
            except RateLimitException:
                self.retry(page=page, client_id=client_id, countdown=60)

        if shipments is None or len(shipments) == 0:
            return
        count = 0
        for id in list(map(lambda x: x['shipmentId'], final_result)):
            task = CreateShipmentData()
            task.apply_async(args=[id, client_id], countdown=count*5)
            count+=1

        task = TaskGetShipmentData()
        task.apply_async(args=[page+1, client_id], countdown=len(final_result)*5)
# For listing API rate limit is 14 calls per minute which translates to an API Call every % secs
# The next page details should be fetched after (no of items in current page *5) seconds (Typically 5 * 50 = 250 Seconds)