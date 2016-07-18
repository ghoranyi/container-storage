from django.conf.urls import url

from . import views

urlpatterns = [
    # API
    url(r'api/register/(?P<node_id>[a-zA-Z0-9\-]+)/?$', views.register_node, name='register_node'),
    url(r'api/snapshot/(?P<node_id>[a-zA-Z0-9\-]+)/?$', views.post_snapshot, name='snapshot'),

    # Misc
    url(r'overview/?$', views.overview, name='overview'),
    url(r'service_interfaces/?$', views.service_interfaces, name='service_interfaces'),
]
