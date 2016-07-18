from django.http import HttpResponse, HttpResponseServerError, HttpResponseNotFound
from django.shortcuts import render
from logging import getLogger

from containerstorage.models import Node, Container, NetworkInterface

import simplejson

# Create your views here.


log = getLogger("containerstorage")


def register_node(request, node_id):
    node = Node.objects.create(node_uuid=node_id)
    log.info("New node registered ({engine})".format(engine=node.node_uuid))
    return HttpResponse(node.node_uuid)


def post_snapshot(request, node_id):

    log.debug("Request from {engine}".format(engine=node_id))

    try:
        node_object = Node.objects.get(node_uuid=node_id)
    except Node.DoesNotExist:
        log.info("Node is not registered. ({node_id})".format(node_id=node_id))
        return HttpResponseNotFound("Node is not registered. (node_id = {node_id})".format(node_id=node_id))

    try:
        body = simplejson.loads(request.body)
        container_ids = [c["Id"] for c in body["containers"]]
        killed_containers = Container.objects.filter(host_node=node_object).exclude(container_id__in=container_ids).delete()
        if killed_containers > 0:
            log.info("{no} containers were killed on {node}".format(no=killed_containers, node=node_object.node_uuid))
        for c in body["containers"]:
            container, created = Container.objects.get_or_create(container_id=c["Id"], host_node=node_object)
            container.image_name = c["Image"]
            container.image_id = c["ImageID"]
            container.save()
            if created:
                log.info("New container detected: {node}/{container}".format(node=node_object.node_uuid, container=container.image_name))
            container_ids = [c["Id"] for c in body["containers"]]
            killed_containers_no, killed_containers = Container.objects.filter(host_node=node_object).exclude(container_id__in=container_ids).delete()
            if killed_containers_no > 0:
                log.info("{no} containers were killed on {node}".format(no=killed_containers_no, node=node_object.node_uuid))
            network_ids = [n_details["EndpointID"] for n_name, n_details in c["NetworkSettings"]["Networks"].iteritems()]
            detached_no, detached_containers = Container.objects.filter(host_node=node_object).exclude(container_id__in=container_ids).delete()
            if killed_containers_no > 0:
                log.info("{no} containers were killed on {node}".format(no=killed_containers_no, node=node_object.node_uuid))
            for network_name, network_details in c["NetworkSettings"]["Networks"].iteritems():
                network, created = NetworkInterface.objects.get_or_create(endpoint_id=network_details["EndpointID"], container=container)
                network.network_name = network_name
                network.network_id = network_details["NetworkID"]
                network.mac_address = network_details["MacAddress"]
                network.ip_address = network_details["IPAddress"]
                network.gateway_address = network_details["Gateway"]
                network.subnet_prefix_len = network_details["IPPrefixLen"]
                network.save()
                if created:
                    log.info("New network interface detected: {node}/{container}/{network}".format(
                        node=node_object.node_uuid,
                        container=container.image_name,
                        network=network.network_name))
        return HttpResponse("OK")

    except simplejson.JSONDecodeError as e:
        log.exception("Unable to parse message: {msg}".format(msg=request.body))
        return HttpResponseServerError("Unable to parse message body")


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
                "interfaces": interfaces
            })
        snapshot.append({
            "name": str(node),
            "containers": containers
        })
    return render(request, 'containerstorage/overview.html', {"snapshot": snapshot})
