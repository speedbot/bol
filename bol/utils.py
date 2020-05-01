import logging


def get_task_logger():
    return logging.getLogger('task_exceptions')


def tuple_instance(instance):
    return (instance._meta.app_label, instance._meta.model_name, instance.id)