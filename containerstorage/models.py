from __future__ import unicode_literals
from datetime import datetime

from django.db import models

from uuidfield import UUIDField

# Create your models here.


class Node(models.Model):
    node_uuid = UUIDField(auto=True)
    host_name = models.CharField(max_length=1000, blank=True)
    docker_version = models.CharField(max_length=15, blank=True)
    last_updated = models.DateTimeField(default=datetime.now)

    @classmethod
    def create(cls):
        obj = cls()
        return obj


class Container(models.Model):
    host_node = models.ForeignKey(Node, on_delete=models.CASCADE)
    image_name = models.CharField(max_length=1000)
    image_id = models.CharField(max_length=300)
    container_id = models.CharField(max_length=300)


class NetworkInterface(models.Model):
    container = models.ForeignKey(Node, on_delete=models.CASCADE)
    network_name = models.CharField(max_length=300)
    network_id = models.CharField(max_length=300)
    mac_address = models.CharField(max_length=17)
    ip_address = models.CharField(max_length=40)
    gateway_address = models.CharField(max_length=40)
    subnet_prefix_length = models.IntegerField(default=0)
