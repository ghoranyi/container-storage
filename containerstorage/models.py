from __future__ import unicode_literals
from datetime import datetime

from django.db import models

# Create your models here.


class Node(models.Model):
    node_uuid = models.CharField(max_length=100, default="")
    host_name = models.CharField(max_length=1000, blank=True)
    docker_version = models.CharField(max_length=15, blank=True)
    last_updated = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return unicode(self.node_uuid)


class Container(models.Model):
    host_node = models.ForeignKey(Node, on_delete=models.CASCADE)
    image_name = models.CharField(max_length=1000)
    image_id = models.CharField(max_length=300)
    container_id = models.CharField(max_length=300)

    def __unicode__(self):
        return unicode(self.image_name)


class NetworkInterface(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    endpoint_id = models.CharField(max_length=100, default="")
    network_name = models.CharField(max_length=300)
    network_id = models.CharField(max_length=300)
    mac_address = models.CharField(max_length=17)
    ip_address = models.CharField(max_length=40)
    gateway_address = models.CharField(max_length=40, blank=True)
    subnet_prefix_length = models.IntegerField(default=0)

    def __unicode__(self):
        return unicode(self.network_name)
