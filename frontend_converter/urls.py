from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'es_query/?$', views.view_es_query),
]
