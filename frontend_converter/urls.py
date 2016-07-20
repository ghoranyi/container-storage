from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'es_query/?$', views.view_es_query),
    url(r'es_response/?$', views.view_es_reponse),
    url(r'visceral/?$', views.view_visceral()),
]
