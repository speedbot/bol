from billiard.exceptions import SoftTimeLimitExceeded
from django.db import DatabaseError, OperationalError
from ratelimit import RateLimitException

from bol.utils import get_api_handler
from celery.task import Task as CeleryTask

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
    def _run(self, shipmentId, *args, **kwargs):
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
            for item in list:
                obj.shipmentItems.add(item)


# Get All items under FBR category
class TaskGetFBRShipments(Task):
    fullfillment_type = 'FBR'

    def _run(self, *args, **kwargs):
        task = TaskGetShipmentData()
        task.delay(self.fullfillment_type, 1)


# Get All items under FBB category
class TaskGetFBBShipments(Task):
    fullfillment_type = 'FBB'

    def _run(self, *args, **kwargs):
        task = TaskGetShipmentData()
        task.delay(self.fullfillment_type, 1)


class TaskGetAllShipments(Task):
    def _run(self, *args, **kwargs):
        task1 = TaskGetFBBShipments()
        task1.delay()
        task2 = TaskGetFBRShipments()
        task2.delay()


# Task to get shipment data and recursively call itself to fetch data of consequent pages
class TaskGetShipmentData(Task):
    def _run(self, fullfillment_method, page, *args, **kwargs):
        params = {
            'fulfilment-method': fullfillment_method,
            'page': page,
        }
        try:
            shipments = get_api_handler().get_shipment_data(params)
        except RateLimitException:
            self.retry(fullfillment_method=fullfillment_method, page=page, countdown=60)
        if shipments is None or len(shipments) == 0:
            return
        for id in list(map(lambda x: x['shipmentId'], shipments['shipments'])):
            task = CreateShipmentData()
            task.apply_async(args=[id], countdown=6*page)

        task = TaskGetShipmentData()
        task.delay(fullfillment_method, page+1)
