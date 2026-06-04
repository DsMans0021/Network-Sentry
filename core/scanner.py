
import threading
import socket
from typing import List, Dict, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from scapy.all import ARP, Ether, srp, IP, ICMP, sr1
from mac_vendor_lookup import MacLookup
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import Config
from utils.helpers import (
    validate_ip,
    calculate_network_range,
    resolve_hostname,
    ping_host,
    format_mac
)
from utils.logger import logger

class NetworkScanner:
    
    def __init__(self):
        self.mac_lookup = MacLookup()
        self.max_threads = Config.MAX_THREADS
        self.timeout = Config.SCAN_TIMEOUT
        self._stop_scan = False
        self._progress_callback = None
    
    def set_progress_callback(self, callback: Callable[[int, int], None]):
        self._progress_callback = callback
    
    def stop_scan(self):
        self._stop_scan = True
    
    def get_network_range(self) -> str:
        try:
            local_ip = self._get_local_ip()
            if local_ip:
                return calculate_network_range(local_ip)
            
            return "192.168.1.0/24"
        except Exception as e:
            logger.error(f"Error detecting network range: {e}")
            return "192.168.1.0/24"
    
    def _get_local_ip(self) -> Optional[str]:
        try:
            interface = Config.DEFAULT_INTERFACE
            if interface:
                ip = Config.get_interface_ip(interface)
                if ip:
                    return ip
            
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return None
    
    def scan_network(self, ip_range: str = None) -> List[Dict]:
        self._stop_scan = False
        
        if ip_range is None:
            ip_range = self.get_network_range()
        
        logger.info(f"Starting network scan for {ip_range}")
        
        try:
            devices = self._arp_scan(ip_range)
            
            for device in devices:
                if not self._stop_scan:
                    device['hostname'] = resolve_hostname(device['ip'], self.timeout)
                    device['vendor'] = self.get_vendor(device['mac'])
            
            logger.info(f"Scan complete. Found {len(devices)} devices.")
            return devices
            
        except Exception as e:
            logger.error(f"Error during network scan: {e}")
            return []
    
    def _arp_scan(self, target_ip: str) -> List[Dict]:
        devices = []
        
        try:
            arp = ARP(pdst=target_ip)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            
            logger.debug(f"Sending ARP request to {target_ip}")
            
            result = srp(packet, timeout=self.timeout, verbose=False)[0]
            
            for sent, received in result:
                if self._stop_scan:
                    break
                
                device = {
                    'ip': received.psrc,
                    'mac': format_mac(received.hwsrc),
                    'hostname': None,
                    'vendor': None
                }
                devices.append(device)
                logger.debug(f"Found device: {device['ip']} - {device['mac']}")
            
        except Exception as e:
            logger.error(f"ARP scan error: {e}")
            devices = self._icmp_scan(target_ip)
        
        return devices
    
    def _icmp_scan(self, target_ip: str) -> List[Dict]:
        devices = []
        
        try:
            import ipaddress
            network = ipaddress.ip_network(target_ip, strict=False)
            
            total_hosts = network.num_addresses - 2
            current = 0
            
            def ping_and_collect(ip_str):
                nonlocal current
                if self._stop_scan:
                    return None
                
                if ping_host(ip_str, self.timeout):
                    device = {
                        'ip': ip_str,
                        'mac': None,
                        'hostname': None,
                        'vendor': None
                    }
                    return device
                return None
            
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                futures = []
                for ip in network.hosts():
                    if self._stop_scan:
                        break
                    futures.append(executor.submit(ping_and_collect, str(ip)))
                
                for future in as_completed(futures):
                    if self._stop_scan:
                        break
                    
                    current += 1
                    if self._progress_callback:
                        self._progress_callback(current, total_hosts)
                    
                    result = future.result()
                    if result:
                        devices.append(result)
        
        except Exception as e:
            logger.error(f"ICMP scan error: {e}")
        
        return devices
    
    def ping_host(self, ip: str) -> bool:
        return ping_host(ip, self.timeout)
    
    def get_hostname(self, ip: str) -> Optional[str]:
        return resolve_hostname(ip, self.timeout)
    
    def get_vendor(self, mac_address: str) -> Optional[str]:
        try:
            if not mac_address:
                return None
            
            cleaned = mac_address.replace(':', '').replace('-', '')[:6].upper()
            
            vendor = self.mac_lookup.lookup(cleaned)
            return vendor if vendor and vendor != "Unknown" else "Unknown"
        except Exception as e:
            logger.debug(f"Vendor lookup error for {mac_address}: {e}")
            return "Unknown"
    
    def arp_scan(self, target_ip: str) -> List[Dict]:
        return self._arp_scan(target_ip)
    
    def scan_single_host(self, ip: str) -> Dict:
        device = {
            'ip': ip,
            'mac': None,
            'hostname': None,
            'vendor': None
        }
        
        try:
            arp = ARP(pdst=ip)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            
            result = srp(packet, timeout=self.timeout, verbose=False)[0]
            
            for sent, received in result:
                device['mac'] = format_mac(received.hwsrc)
                break
        except Exception:
            pass
        
        device['hostname'] = resolve_hostname(ip, self.timeout)
        
        if device['mac']:
            device['vendor'] = self.get_vendor(device['mac'])
        
        return device
    
    def concurrent_scan(self, ip_list: List[str]) -> List[Dict]:
        devices = []
        total = len(ip_list)
        current = 0
        
        def scan_ip(ip_str):
            nonlocal current
            if self._stop_scan:
                return None
            
            device = self.scan_single_host(ip_str)
            current += 1
            
            if self._progress_callback:
                self._progress_callback(current, total)
            
            return device if device['mac'] else None
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(scan_ip, ip) for ip in ip_list]
            
            for future in as_completed(futures):
                if self._stop_scan:
                    break
                
                result = future.result()
                if result:
                    devices.append(result)
        
        return devices
