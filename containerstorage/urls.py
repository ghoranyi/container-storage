from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'api/snapshot/(?P<engine_id>.+)/?$', views.post_snapshot, name='snapshot'),
]
