from containerstorage.models import Service
from containerstorage.utils import get_service_ips
from django.http.response import JsonResponse


def view_es_query(request):
    return JsonResponse(_generate_es_query())


def _generate_es_query():
    query_object = {"size": 0, "query": {
        "constant_score": {
            "filter": {
                "term": {
                    "direction": "in"
                }
            }
        }
    }}

    filters = {}
    for service in Service.objects.all():
        service_filter = {}
        interfaces = get_service_ips(service)
        service_filter["terms"] = {
            "ip": interfaces
        }
        filters[service.name] = service_filter

    query_object["aggregations"] = {
        "services": {
            "filters": {
                "filters": filters
            },
            "aggregations": {
                "client_ips": {
                    "terms": {
                        "field": "client_ip"
                    },
                    "aggregations": {
                        "status": {
                            "range": {
                                "field": "http.code",
                                "ranges": [
                                    {"from": 200, "to": 299},
                                    {"from": 300, "to": 399},
                                    {"from": 400, "to": 499},
                                    {"from": 500, "to": 599}
                                ]
                            }
                        }
                    }
                }
            }
        }
    }

    return query_object
