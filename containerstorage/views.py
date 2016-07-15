from django.http import HttpResponse, HttpResponseServerError, HttpResponseNotFound
from django.shortcuts import render
from logging import getLogger

from containerstorage.models import Node

import simplejson

# Create your views here.


log = getLogger("containerstorage")


def register_node(request):
    node = Node.create()
    node.save()
    log.info("New node registered ({engine})".format(engine=node.node_id))
    return HttpResponse(node.node_id)


def post_snapshot(request, node_id):

    log.debug("Request from {engine}".format(engine=node_id))

    try:
        node_object = Node.objects.get(node_id=node_id)
    except Node.DoesNotExist:
        log.info("Node is not registered. ({node_id})".format(node_id=node_id))
        return HttpResponseNotFound("Node is not registered. (node_id = {node_id})".format(node_id=node_id))

    try:
        body = simplejson.loads(request.body)
        container_names = [c["Image"] for c in body["containers"]]
        log.info("{engine}: {containers}".format(engine=engine_id, containers=container_names))
        return HttpResponse("OK")

    except simplejson.JSONDecodeError as e:
        log.exception("Unable to parse message: {msg}".format(msg=request.body))
        return HttpResponseServerError("Unable to parse message body")
