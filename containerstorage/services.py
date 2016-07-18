from logging import getLogger

from containerstorage.models import Container, Service

log = getLogger(containerstorage.services)


def container_updated(container_details, container):
    service_name = _get_service_name(container_details)
    if service_name:
        service, created = Service.objects.get_or_create(name=service_name)
        if created:
            log.info("New service detected: {service}".format(sevice=str(service)))
        if container.service is not None and container.service != service:
            container_will_be_removed(container)
        container.service = service
        container.save()


def container_will_be_removed(container):
    if Container.objects.filter(service=container.service).count() <= 1:
        log.info("Service removed: {service}".format(service=str(service)))
    pass


def _get_service_name(container_details):
    # docker-compose service
    labels = container_details["Labels"]
    COMPOSE_SERVICE_LABEL_KEY = "com.docker.compose.service"
    if COMPOSE_SERVICE_LABEL_KEY in labels:
        return labels[COMPOSE_SERVICE_LABEL_KEY]
    return None
