from __future__ import unicode_literals
from datetime import datetime

from django.db import models

# Create your models here.


class Node(models.Model):
    engine_id = models.CharField(max_length=200)
    host_name = models.CharField(max_length=1000, blank=True)
    docker_version = models.CharField(max_length=15, blank=True)
    last_updated = models.DateTimeField(default=datetime.now)


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
