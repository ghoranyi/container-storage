from containerstorage.models import Service
from containerstorage.utils import get_service_ips, get_service_for_ip
from django.conf import settings
from django.http.response import JsonResponse
from elasticsearch import Elasticsearch
import simplejson
import time


def view_es_query(request):
    return JsonResponse(_generate_es_query())


def view_es_reponse(request):
    url = settings.ELASTIC_URL
    query = _generate_es_query()
    es = Elasticsearch(url)
    res = es.search(body=query)
    return JsonResponse(res)

def view_visceral(request):
    return JsonResponse(_generate_visceral_input())


def _get_dummy_es_response():
    dummy_response = '{"hits": {"hits": [], "total": 19, "max_score": 0.0}, "_shards": {"successful": 17, "failed": 0, "total": 17}, "took": 18, "aggregations": {"services": {"buckets": {"nginx": {"client_ips": {"buckets": [], "sum_other_doc_count": 0, "doc_count_error_upper_bound": 0}, "doc_count": 0}, "counter": {"client_ips": {"buckets": [{"status": {"buckets": [{"from": 200.0, "from_as_string": "200.0", "to_as_string": "299.0", "doc_count": 12, "to": 299.0, "key": "200.0-299.0"}, {"from": 300.0, "from_as_string": "300.0", "to_as_string": "399.0", "doc_count": 0, "to": 399.0, "key": "300.0-399.0"}, {"from": 400.0, "from_as_string": "400.0", "to_as_string": "499.0", "doc_count": 0, "to": 499.0, "key": "400.0-499.0"}, {"from": 500.0, "from_as_string": "500.0", "to_as_string": "599.0", "doc_count": 0, "to": 599.0, "key": "500.0-599.0"}]}, "key": "10.0.11.3", "doc_count": 12}], "sum_other_doc_count": 0, "doc_count_error_upper_bound": 0}, "doc_count": 12}, "frontend": {"client_ips": {"buckets": [{"status": {"buckets": [{"from": 200.0, "from_as_string": "200.0", "to_as_string": "299.0", "doc_count": 4, "to": 299.0, "key": "200.0-299.0"}, {"from": 300.0, "from_as_string": "300.0", "to_as_string": "399.0", "doc_count": 0, "to": 399.0, "key": "300.0-399.0"}, {"from": 400.0, "from_as_string": "400.0", "to_as_string": "499.0", "doc_count": 0, "to": 499.0, "key": "400.0-499.0"}, {"from": 500.0, "from_as_string": "500.0", "to_as_string": "599.0", "doc_count": 0, "to": 599.0, "key": "500.0-599.0"}]}, "key": "10.0.11.4", "doc_count": 4}], "sum_other_doc_count": 0, "doc_count_error_upper_bound": 0}, "doc_count": 4}}}}, "timed_out": false}'
    return simplejson.loads(dummy_response)


def _generate_visceral_input():
    input = {
        "renderer": "global",
        "name": "edge",
        "nodes": [
            {
                "renderer": "region",
                "name": "INTERNET",
                "updated": int(time.time()),
                "nodes": [],
                "class": "normal"
            },
            {
                "renderer": "region",
                "name": "eu-west-1",
                "class": "normal",
                "updated": int(time.time()),
                "nodes": [
                    {
                        "name": "INTERNET",
                        "class": "normal"
                    }
                ],
                "connections": []
            }
        ],
        "connections": [
            {
                "source": "INTERNET",
                "target": "eu-west-1",
                "metrics": {
                    "normal": 100,
                },
                "notices": [

                ],
                "class": "normal"
            }
        ]
    }
    service_nodes = set()
    connections = []
    es_response = _get_dummy_es_response()
    for service_name, service_details in es_response["aggregations"]["services"]["buckets"].iteritems():
        service_nodes.add(service_name)
        for client_ip_bucket in service_details["client_ips"]["buckets"]:
            client_ip = client_ip_bucket["key"]
            client_service_name = get_service_for_ip(client_ip).name
            requests = client_ip_bucket["doc_count"]
            service_nodes.add(client_service_name)
            connections.append({
                "source": client_service_name,
                "target": service_name,
                "metrics": {
                    "normal": int(requests),
                },
                "class": "normal"
            })
    service_node_definitions = [
        {
            "name": x,
            "class": "normal"
        } for x in service_nodes
    ]
    service_node_definitions.append({
        "name": "INTERNET",
        "class": "normal"
    })

    input = {
        "renderer": "global",
        "name": "edge",
        "nodes": [
            {
                "renderer": "region",
                "name": "INTERNET",
                "updated": int(time.time()),
                "nodes": [],
                "class": "normal"
            },
            {
                "renderer": "region",
                "name": "eu-west-1",
                "class": "normal",
                "updated": int(time.time()),
                "nodes": service_node_definitions,
                "connections": connections
            }
        ],
        "connections": [
            {
                "source": "INTERNET",
                "target": "eu-west-1",
                "metrics": {
                    "normal": 100,
                },
                "notices": [

                ],
                "class": "normal"
            }
        ]
    }
    return input

def _generate_es_query():
    query_object = {"size": 0, "query": {
        "constant_score": {
            "filter": {
                "and": [
                    {"term": {"direction": "in"}},
                    {"range": {"@timestamp": {"gt": "now-10m"}}}
                ]
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
