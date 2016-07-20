from containerstorage.models import NetworkInterface, NetworkInterfaceNode


def get_service_ips_and_subnets(service):
    return map(
        lambda net: (net.ip_address, net.subnet_prefix_length),
        list(NetworkInterface.objects.filter(container__service=service))
    )


def get_internal_ips_and_subnets(service):
    return map(
        lambda net: (net.ip_address, net.subnet_prefix_length, net.container.host_name),
        list(NetworkInterfaceNode.objects.filter(container__service=service))
    )


def get_service_ips(service):
    return map(
        lambda net: net.ip_address,
        list(NetworkInterface.objects.filter(container__service=service))
    )


def get_internal_ips(service):
    return map(
        lambda net: (net.ip_address, net.container.host_name),
        list(NetworkInterfaceNode.objects.filter(container__service=service))
    )


def get_service_for_ip(ip):
    try:
        interface = NetworkInterfaceNode.objects.get(ip_address=ip)
        return interface.container.service
    except NetworkInterfaceNode.DoesNotExist:
        return None
