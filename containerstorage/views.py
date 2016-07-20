from datetime import datetime
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import render
from logging import getLogger

from containerstorage.models import Node, Container, NetworkInterface, NetworkInterfaceNode, Service
from containerstorage.utils import get_service_ips_and_subnets

import simplejson


log = getLogger("containerstorage")


def register_node(request, node_id):
    node = Node.objects.create(node_uuid=node_id)
    log.info("New node registered ({engine})".format(engine=node.node_uuid))
    return HttpResponse(node.node_uuid)


def post_snapshot(request, node_id):
    """
    Snapshot json contains two sections: "containers" and "networks"

    "containers" lists all basic containers information, e.g. `docker ps` for all nodes
    "networks" lists all networks for all containers, including those that map external IPs
    """

    log.debug("Request from {engine}".format(engine=node_id))

    node_object = _get_node(node_id)

    try:
        body = simplejson.loads(request.body)
        _remove_killed_containers(body, node_object)
        # handle "containers" section
        for c in body["containers"]:
            container, created = Container.objects.get_or_create(container_id=c["Id"], host_node=node_object)
            _update_container(c, container)
            if created:
                log.info("New container detected: {node}/{container}".format(
                    node=node_object.node_uuid, container=container.image_name))
            _remove_disconnected_networks(c["NetworkSettings"]["Networks"], container, ni_model=NetworkInterface)
            for network_name, network_details in c["NetworkSettings"]["Networks"].iteritems():
                network, created = NetworkInterface.objects.get_or_create(
                    endpoint_id=network_details["EndpointID"], container=container)
                _update_network(network, network_details, network_name)
                if created:
                    log.info("New network interface detected: {node}/{container}/{network}".format(
                        node=node_object.node_uuid,
                        container=container.image_name,
                        network=network.network_name))
        # handle "networks" section
        for cid, data in body.get("networks", {}).iteritems():
            container = Container.objects.filter(container_id=cid).first()

            if not container:
                log.warn("Agent posted json with non-existing container id %s in 'networks' section", cid)
                continue

            container.host_name = data["hostname"]
            container.save()
            _remove_disconnected_networks(data["networks"], container, ni_model=NetworkInterfaceNode)
            for network_id, network_details in data["networks"].iteritems():
                network, created = NetworkInterfaceNode.objects.get_or_create(
                    endpoint_id=network_details["EndpointID"], network_id=network_id, container=container)
                _update_network_node(network, network_details)

        return HttpResponse("OK")

    except simplejson.JSONDecodeError:
        log.exception("Unable to parse message: {msg}".format(msg=request.body))
        return HttpResponseServerError("Unable to parse message body")


def _update_network(network, network_details, network_name):
    network.network_name = network_name
    network.network_id = network_details["NetworkID"]
    network.mac_address = network_details["MacAddress"]
    network.ip_address = network_details["IPAddress"]
    network.gateway_address = network_details["Gateway"]
    network.subnet_prefix_length = network_details["IPPrefixLen"]
    network.save()


def _update_network_node(network, network_details):
    network.network_name = network_details["Name"]
    network.mac_address = network_details["MacAddress"]
    network.ip6_address = network_details["IPv6Address"]
    ipv4, subnet_len = network_details["IPv4Address"].split("/")
    network.ip_address = ipv4
    network.subnet_prefix_length = subnet_len
    network.save()


def _update_container(c, container, hostname=None):
    container.image_name = c["Image"]
    container.image_id = c["ImageID"]
    container.service_name = _get_service_name(c)
    container.save()


def _get_node(node_id):
    try:
        node_object = Node.objects.get(node_uuid=node_id)
        node_object.last_updated = datetime.now()
        node_object.save()
        return node_object
    except Node.DoesNotExist:
        log.info("Node is not registered. ({node_id})".format(node_id=node_id))
        raise Http404("Node is not registered. (node_id = {node_id})".format(node_id=node_id))


def _remove_killed_containers(body, node_object):
    container_ids = [c["Id"] for c in body["containers"]]
    killed_containers_no, killed_containers = Container.objects.filter(
        host_node=node_object).exclude(container_id__in=container_ids).delete()
    if killed_containers_no > 0:
        log.info("{no} containers were killed on {node}".format(no=killed_containers_no, node=node_object.node_uuid))


def _remove_disconnected_networks(networks, container, ni_model):
    network_ids = [n_details["EndpointID"] for n_name, n_details in networks.iteritems()]
    detached_no, detached_list = ni_model.objects.filter(
        container=container).exclude(endpoint_id__in=network_ids).delete()
    if detached_no > 0:
        log.info("{no} interfaces were disconnected from {container}".format(no=detached_no, container=str(container)))


def _get_service_name(container_details):
    # docker-compose service
    labels = container_details["Labels"]
    COMPOSE_SERVICE_LABEL_KEY = "com.docker.compose.service"
    if COMPOSE_SERVICE_LABEL_KEY in labels:
        return labels[COMPOSE_SERVICE_LABEL_KEY]
    return None


def overview(request):
    snapshot = list()
    for node in Node.objects.all():
        containers = list()
        for container in Container.objects.filter(host_node=node):
            interfaces = map(
                lambda x: {
                    "ip_address": x.ip_address,
                    "network_name": x.network_name
                },
                list(NetworkInterface.objects.filter(container=container)))
            containers.append({
                "name": str(container),
                "service": str(container.service),
                "interfaces": interfaces
            })
        snapshot.append({
            "name": str(node),
            "containers": containers
        })
    return render(request, 'containerstorage/overview.html', {"snapshot": snapshot})


def service_interfaces(request):
    services = list()
    for service in Service.objects.all():
        interfaces = get_service_ips_and_subnets(service)
        services.append({
            "name": str(service),
            "networks": interfaces
        })
    return render(request, 'containerstorage/service_interfaces.html', {"services": services})
