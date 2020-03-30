"""
Script to fetch Office365 IPs and present them for use in ASA ACLs
"""

import uuid
import requests
import ipaddress


def generate_guid():
    """Randomly generate new GUID at runtime."""
    id = str(uuid.uuid4())
    return id


def get_o365_ips(services, IPv6):
    """Fetch Office365 IP-addresses for selected services."""
    base_url = "https://endpoints.office.com/endpoints/worldwide"
    guid = generate_guid()
    service_list = ",".join(services)
    NoIPv6 = str(not IPv6)

    # assemble url
    request_url = f"{base_url}?clientrequestid={guid}&services={service_list}&NoIPV6={NoIPv6}"

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


def ipList_to_objectGroup(ip_list):
    """Translate IP prefix list to ASA network object-group."""
    object_group = list()
    object_group.append("object-group network o365_addresses")
    
    for ip in ip_list:
        network, mask = prefix_to_network(ip)
        object_entry = f"  network-object {network} {mask}"
        object_group.append(object_entry)

    return object_group

if __name__ == '__main__':
    services = [ "Skype" ]  # allowed values: <Common | Exchange | SharePoint | Skype>
    IPv6 = False  # allowed values: <True | False> 

    response = get_o365_ips(services, IPv6)

    ips = parse_response(response)

    print("\n".join(ipList_to_objectGroup(ips)))

    #test_ip = "192.0.2.0/24"
    #print(prefix_to_network(test_ip))
