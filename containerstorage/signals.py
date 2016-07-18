from logging import getLogger

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from containerstorage.models import Container, Service

log = getLogger("containerstorage.signals")


@receiver(post_delete, sender=Container)
def remove_empty_services(sender, instance, **kwargs):
    try:
        _check_if_service_needs_to_be_removed(instance.service)
    except Service.DoesNotExist:
        pass


@receiver(pre_save, sender=Container)
def container_updated(sender, instance, **kwargs):
    if instance.service_name:
        service, created = Service.objects.get_or_create(name=instance.service_name)
        if created:
            log.info("New service detected: {service}".format(service=str(service)))
        if instance.service is not None and instance.service != service:
            _check_if_service_needs_to_be_removed(instance.service)
        instance.service = service


def _check_if_service_needs_to_be_removed(service):
    if not Container.objects.filter(service=service).count():
        service.delete()
