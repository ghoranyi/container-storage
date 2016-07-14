from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from logging import getLogger

from models import Node

import simplejson

# Create your views here.


log = getLogger("containerstorage")


def post_snapshot(request, engine_id):

    log.debug("Request from {engine}".format(engine=engine_id))

    node_object, created = Node.objects.get_or_create(engine_id=engine_id)
    if created:
        log.info("New engine registered ({engine})".format(engine=engine_id))

    try:
        body = simplejson.loads(request.body)
        container_names = [c["Image"] for c in body["containers"]]
        log.info("{engine}: {containers}".format(engine=engine_id, containers=container_names))
        return HttpResponse("OK")

    except simplejson.JSONDecodeError as e:
        log.error("Unable to parse message: {msg}".format(msg=request.body))
        return HttpResponseServerError("Unable to parse message body")
