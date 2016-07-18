from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from containerstorage.models import Container, Service


@receiver(post_delete, sender=Container)
def remove_empty_services(sender, instance, **kwargs):
    _check_if_service_needs_to_be_removed(instance.service)


@receiver(pre_save, sender=Container)
def container_updated(sender, instance, **kwargs):
    if instance.service_name:
        service, created = Service.objects.get_or_create(name=service_name)
        if created:
            log.info("New service detected: {service}".format(service=str(service)))
        if container.service is not None and container.service != service:
            _check_if_service_needs_to_be_removed(container.service)
        container.service = service


def _check_if_service_needs_to_be_removed(service):
    try:
        if not Container.objects.filter(service=service).count():
            service.delete()
    except Service.DoesNotExist:
        pass
