from billiard.exceptions import SoftTimeLimitExceeded
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, OperationalError
from ratelimit import RateLimitException

from bol.utils import get_api_handler
from celery.schedules import crontab
from celery.task import PeriodicTask as CeleryPeriodicTask
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


class RefetchModelTask(Task):
    """
    Task that takes app label, model name and an id.
    """
    def get_instance(self, app_label, model_name, id):
        model = apps.get_model(app_label, model_name)
        return model.objects.all().get(pk=id)

    def run(self, app_label, model_name, id, *args, **kwargs):
        try:
            instance = self.get_instance(app_label, model_name, id)
        except (ObjectDoesNotExist, OperationalError, DatabaseError) as exc:
            raise self.retry(exc=exc)

        return super(RefetchModelTask, self).run(instance, *args, **kwargs)


class PeriodicTask(TaskBase, CeleryPeriodicTask):
    """
    Base periodic task for tasks that hit up the database.
    """
    run_every = crontab(
        minute='0',
        hour='0',
        day_of_month='1',
        month_of_year='1',
    )

    def _run(self, *args, **kwargs):
        pass


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


class TaskGetAllShipments(Task):
    def _run(self, *args, **kwargs):
        try:
            shipments = get_api_handler().get_all_shipments()
        except RateLimitException:
            self.retry(countdown=60)
        if shipments is None:
            return
        for id in list(map(lambda x: x['shipmentId'], shipments['shipments'])):
            task = CreateShipmentData()
            task.delay(id)
