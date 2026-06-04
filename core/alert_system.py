
from typing import List, Dict, Optional
from datetime import datetime
from colorama import Fore, Style, init
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import Config
from core.database import DatabaseManager
from utils.logger import logger

init(autoreset=True)

class AlertSystem:
    
    NEW_DEVICE = "NEW_DEVICE"
    KNOWN_DEVICE_RETURNED = "KNOWN_DEVICE_RETURNED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    
    def __init__(self):
        self.db = DatabaseManager()
        self.alert_on_new = Config.ALERT_ON_NEW_DEVICE
        self.alert_on_returned = Config.ALERT_ON_KNOWN_RETURNED
        self.alert_on_suspicious = Config.ALERT_ON_SUSPICIOUS
    
    def check_new_devices(self, current_devices: List[Dict], known_devices: List[Dict]) -> List[Dict]:
        known_macs = {device['mac_address'] for device in known_devices if device['mac_address']}
        
        new_devices = []
        for device in current_devices:
            if device.get('mac') and device['mac'] not in known_macs:
                new_devices.append(device)
        
        return new_devices
    
    def check_returned_devices(self, current_devices: List[Dict], known_devices: List[Dict]) -> List[Dict]:
        current_macs = {device.get('mac') for device in current_devices if device.get('mac')}
        known_macs = {device['mac_address'] for device in known_devices if device['mac_address']}
        
        returned = []
        for device in known_devices:
            if device['mac_address'] in current_macs:
                returned.append(device)
        
        return returned
    
    def send_alert(self, device: Dict, alert_type: str):
        db_device = self.db.get_device_by_mac(device.get('mac'))
        device_id = db_device['id'] if db_device else None
        
        message = self._create_alert_message(device, alert_type)
        
        self.log_alert(device, alert_type, message)
        
        if device_id:
            self.db.add_alert(device_id, alert_type, message)
        
        self._console_alert(device, alert_type, message)
    
    def _create_alert_message(self, device: Dict, alert_type: str) -> str:
        ip = device.get('ip', 'Unknown')
        mac = device.get('mac', 'Unknown')
        hostname = device.get('hostname', 'Unknown')
        vendor = device.get('vendor', 'Unknown')
        
        if alert_type == self.NEW_DEVICE:
            return f"New device detected: {ip} ({mac}) - {hostname} [{vendor}]"
        elif alert_type == self.KNOWN_DEVICE_RETURNED:
            return f"Known device returned: {ip} ({mac}) - {hostname}"
        elif alert_type == self.SUSPICIOUS_ACTIVITY:
            return f"Suspicious activity from: {ip} ({mac}) - {hostname}"
        else:
            return f"Alert: {alert_type} for device {ip}"
    
    def _console_alert(self, device: Dict, alert_type: str, message: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if alert_type == self.NEW_DEVICE:
            print(f"{Fore.RED}[{timestamp}] {message}{Style.RESET_ALL}")
        elif alert_type == self.KNOWN_DEVICE_RETURNED:
            print(f"{Fore.GREEN}[{timestamp}] {message}{Style.RESET_ALL}")
        elif alert_type == self.SUSPICIOUS_ACTIVITY:
            print(f"{Fore.YELLOW}[{timestamp}] {message}{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}[{timestamp}] {message}{Style.RESET_ALL}")
    
    def log_alert(self, device: Dict, alert_type: str, message: str):
        logger.log_alert(alert_type, device, message)
    
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        return self.db.get_alert_history(limit)
    
    def process_scan_results(self, devices: List[Dict]):
        known_devices = self.db.get_all_devices()
        
        new_devices = self.check_new_devices(devices, known_devices)
        
        for device in new_devices:
            if self.alert_on_new:
                self.send_alert(device, self.NEW_DEVICE)
    
    def monitor_devices(self, devices: List[Dict]):
        known_devices = self.db.get_all_devices()
        
        returned_devices = self.check_returned_devices(devices, known_devices)
        
        for device in returned_devices:
            if self.alert_on_returned:
                scan_device = {
                    'ip': device['ip_address'],
                    'mac': device['mac_address'],
                    'hostname': device['hostname'],
                    'vendor': device['vendor']
                }
                self.send_alert(scan_device, self.KNOWN_DEVICE_RETURNED)
    
    def print_alert_summary(self, alerts: List[Dict]):
        if not alerts:
            print(f"{Fore.CYAN}No alerts in history.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"ALERT HISTORY (Last {len(alerts)} alerts)")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        for alert in alerts:
            timestamp = alert['timestamp']
            alert_type = alert['alert_type']
            message = alert['message']
            ip = alert.get('ip_address', 'N/A')
            
            if alert_type == self.NEW_DEVICE:
                color = Fore.RED
            elif alert_type == self.KNOWN_DEVICE_RETURNED:
                color = Fore.GREEN
            elif alert_type == self.SUSPICIOUS_ACTIVITY:
                color = Fore.YELLOW
            else:
                color = Fore.BLUE
            
            print(f"{color}[{timestamp}] {alert_type}")
            print(f"  IP: {ip}")
            print(f"  Message: {message}{Style.RESET_ALL}\n")
    
    def enable_alert(self, alert_type: str):
        if alert_type == self.NEW_DEVICE:
            self.alert_on_new = True
        elif alert_type == self.KNOWN_DEVICE_RETURNED:
            self.alert_on_returned = True
        elif alert_type == self.SUSPICIOUS_ACTIVITY:
            self.alert_on_suspicious = True
    
    def disable_alert(self, alert_type: str):
        if alert_type == self.NEW_DEVICE:
            self.alert_on_new = False
        elif alert_type == self.KNOWN_DEVICE_RETURNED:
            self.alert_on_returned = False
        elif alert_type == self.SUSPICIOUS_ACTIVITY:
            self.alert_on_suspicious = False
    
    def get_alert_settings(self) -> Dict[str, bool]:
        return {
            'new_device': self.alert_on_new,
            'known_device_returned': self.alert_on_returned,
            'suspicious_activity': self.alert_on_suspicious
        }
