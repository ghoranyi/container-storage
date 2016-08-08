from containerstorage.models import NetworkInterface, NetworkInterfaceNode, Container


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
    interface = NetworkInterfaceNode.objects.filter(ip_address=ip).first()
    if interface:
        return interface.container.service
    else:
        return None


def get_service_name(host):
    container = Container.objects.filter(host_name=host).first()
    return container.service_name if container else None
