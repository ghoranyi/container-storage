from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'es_query/?$', views.view_es_query),
    url(r'es_response/?$', views.view_es_response),
    url(r'es_query_external/?$', views.view_es_query_external),
    url(r'es_response_external/?$', views.view_es_response_external),
    url(r'vizceral/?$', views.view_vizceral),
]
