from containerstorage.models import NetworkInterface


def get_service_ips_and_subnets(service):
    return map(
        lambda net: (net.ip_address, net.subnet_prefix_length),
        list(NetworkInterface.objects.filter(container__service=service))
    )
