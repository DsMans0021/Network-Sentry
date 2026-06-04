
import re
import socket
import platform
import subprocess
from datetime import datetime
from typing import Optional, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import Config

def validate_ip(ip_address: str) -> bool:
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    match = re.match(pattern, ip_address)
    
    if not match:
        return False
    
    for octet in match.groups():
        if int(octet) < 0 or int(octet) > 255:
            return False
    
    return True

def validate_mac(mac_address: str) -> bool:
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac_address))

def format_bytes(bytes_value: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def get_current_timestamp() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def clear_screen():
    system = platform.system()
    if system == 'Windows':
        subprocess.run('cls', shell=True)
    else:
        subprocess.run('clear', shell=True)

def print_banner():
    print(banner)

def get_interface_ip(interface_name: str) -> Optional[str]:
    return Config.get_interface_ip(interface_name)

def calculate_network_range(ip: str, subnet_mask: str = '255.255.255.0') -> str:
    try:
        if '.' in subnet_mask:
            mask_octets = subnet_mask.split('.')
            cidr = sum(bin(int(octet)).count('1') for octet in mask_octets)
        else:
            cidr = int(subnet_mask.replace('/', ''))
        
        ip_octets = [int(x) for x in ip.split('.')]
        mask_octets = [int(x) for x in subnet_mask.split('.')]
        
        network_octets = []
        for i in range(4):
            network_octets.append(str(ip_octets[i] & mask_octets[i]))
        
        network_ip = '.'.join(network_octets)
        return f"{network_ip}/{cidr}"
    except Exception:
        ip_parts = ip.split('.')
        if len(ip_parts) == 4:
            return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        return "192.168.1.0/24"

def resolve_hostname(ip: str, timeout: int = 2) -> Optional[str]:
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except (socket.herror, socket.timeout):
        return None

def ping_host(ip: str, timeout: int = 2) -> bool:
    system = platform.system()
    
    try:
        if system == 'Windows':
            result = subprocess.run(
                ['ping', '-n', '1', '-w', str(timeout * 1000), ip],
                capture_output=True,
                timeout=timeout + 1
            )
            return result.returncode == 0
        else:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(timeout), ip],
                capture_output=True,
                timeout=timeout + 1
            )
            return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False

def format_mac(mac_address: str) -> str:
    cleaned = re.sub(r'[:-]', '', mac_address.upper())
    
    if len(cleaned) == 12:
        return ':'.join([cleaned[i:i+2] for i in range(0, 12, 2)])
    
    return mac_address

def get_local_ip() -> Optional[str]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None

def parse_cidr(cidr: str) -> Tuple[str, int]:
    if '/' in cidr:
        ip, prefix = cidr.split('/')
        return ip, int(prefix)
    return cidr, 24

def is_ip_in_range(ip: str, network: str) -> bool:
    try:
        import ipaddress
        return ipaddress.ip_address(ip) in ipaddress.ip_network(network)
    except (ImportError, ValueError):
        network_ip, prefix = parse_cidr(network)
        if prefix == 24:
            ip_parts = ip.split('.')
            net_parts = network_ip.split('.')
            return ip_parts[0:3] == net_parts[0:3]
        return False
