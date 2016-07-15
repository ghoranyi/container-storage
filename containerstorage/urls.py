from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'api/register/?$', views.register_node, name='register_node'),
    url(r'api/snapshot/(?P<engine_id>.+)/?$', views.post_snapshot, name='snapshot'),
]
