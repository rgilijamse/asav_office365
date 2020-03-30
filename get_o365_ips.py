"""
Script to fetch Office365 IPs and present them for use in ASA ACLs
"""
import uuid
import ipaddress
import requests


def generate_guid():
    """Randomly generate new GUID at runtime."""
    uid = str(uuid.uuid4())
    return uid


def assemble_url(services, IPv6):
    """Assemble Office365 enpoint query URL for selected services."""
    base_url = "https://endpoints.office.com/endpoints/worldwide"
    guid = generate_guid()
    service_list = ",".join(services)
    no_ipv6 = str(not IPv6)

    # assemble url
    full_url = f"{base_url}?clientrequestid={guid}&ServiceAreas={service_list}&NoIPV6={no_ipv6}"
    return full_url


def get_o365_ips(services, IPv6):
    """Fetch Office365 IP-addresses for selected services."""
    request_url = assemble_url(services, IPv6)

    # fetch IPs
    response = requests.get(request_url)
    if response.status_code == 200:
        content = response.json()
    else:
        raise Exception("IP fetch failed")

    return content


def parse_response(response):
    """Parse Office365 Endpoints API results to a list of IP addresses."""
    ip_list = list()
    for entry in response:
        if 'ips' in entry:  # ignore everything that isn't an IP
            ip_list += entry['ips']
    return ip_list


def prefix_to_network(prefix):
    """Convert an IP prefix to an IP-address and network mask."""
    ipaddr = ipaddress.ip_interface(prefix)  # turn into ipaddress object
    address = ipaddr.ip
    mask = ipaddr.netmask
    return address, mask


def ip_list_to_object_group(ip_list):
    """Translate IP prefix list to ASA network object-group."""
    object_group = list()
    object_group.append("object-group network o365_addresses")

    for ip in ip_list:
        network, mask = prefix_to_network(ip)
        object_entry = f"  network-object {network} {mask}"
        object_group.append(object_entry)

    return object_group

if __name__ == '__main__':
    SERVICES = ["Skype"]  # allowed values: <Common | Exchange | SharePoint | Skype>
    IPV6 = False  # allowed values: <True | False>

    o365_ips = get_o365_ips(SERVICES, IPV6)
    prefix_list = parse_response(o365_ips)

    print("\n".join(ip_list_to_object_group(prefix_list)))

    #test_ip = "192.0.2.0/24"
    #print(prefix_to_network(test_ip))
