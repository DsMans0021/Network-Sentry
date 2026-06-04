
import os
import psutil
import socket
from pathlib import Path

class Config:
    
    DB_PATH = "network_sentry.db"
    
    DEFAULT_INTERFACE = None
    SCAN_INTERVAL = 300
    SCAN_TIMEOUT = 2
    MAX_THREADS = 50
    
    ALERT_ON_NEW_DEVICE = True
    ALERT_ON_KNOWN_RETURNED = True
    ALERT_ON_SUSPICIOUS = True
    
    LOG_FILE = "network_sentry.log"
    LOG_MAX_SIZE = 10 * 1024 * 1024
    LOG_BACKUP_COUNT = 5
    LOG_LEVEL = "INFO"
    
    KNOWN_DEVICES_FILE = "known_devices.json"
    
    EXPORT_DIR = "exports"
    
    BANNER_COLOR = "cyan"
    SUCCESS_COLOR = "green"
    WARNING_COLOR = "yellow"
    ERROR_COLOR = "red"
    INFO_COLOR = "blue"
    
    @staticmethod
    def get_default_interface():
        try:
            gateways = netifaces.gateways()
            default_gateway = gateways.get('default')
            
            if default_gateway and netifaces.AF_INET in default_gateway:
                gateway_ip, interface = default_gateway[netifaces.AF_INET]
                return interface
            
            for interface in netifaces.interfaces():
                if interface != 'lo' and not interface.startswith('lo'):
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        return interface
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def get_interface_ip(interface_name):
        try:
            addrs = psutil.net_if_addrs()
            if interface_name in addrs:
                for addr in addrs[interface_name]:
                    if addr.family == socket.AF_INET:
                        return addr.address
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_project_root():
        return Path(__file__).parent.absolute()
    
    @staticmethod
    def get_db_path():
        return Config.get_project_root() / Config.DB_PATH
    
    @staticmethod
    def get_log_path():
        return Config.get_project_root() / Config.LOG_FILE
    
    @staticmethod
    def get_known_devices_path():
        return Config.get_project_root() / Config.KNOWN_DEVICES_FILE
    
    @staticmethod
    def get_export_dir():
        export_path = Config.get_project_root() / Config.EXPORT_DIR
        export_path.mkdir(exist_ok=True)
        return export_path

Config.DEFAULT_INTERFACE = Config.get_default_interface()
