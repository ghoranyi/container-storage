from django.contrib import admin

from .models import Node, Container, NetworkInterface

# Register your models here.


admin.site.register(Node)
admin.site.register(Container)
admin.site.register(NetworkInterface)
