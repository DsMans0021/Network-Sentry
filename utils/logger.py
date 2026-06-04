
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import Config

class Logger:
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.logger = logging.getLogger('NetworkSentry')
        self.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        if not self.logger.handlers:
            self._setup_file_handler()
            self._setup_console_handler()
        
        self._initialized = True
    
    def _setup_file_handler(self):
        log_path = Config.get_log_path()
        
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=Config.LOG_MAX_SIZE,
            backupCount=Config.LOG_BACKUP_COUNT
        )
        file_handler.setLevel(logging.DEBUG)
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def log_scan_event(self, device_info: dict):
        message = (
            f"Scan Event - IP: {device_info.get('ip_address', 'N/A')}, "
            f"MAC: {device_info.get('mac_address', 'N/A')}, "
            f"Hostname: {device_info.get('hostname', 'N/A')}, "
            f"Vendor: {device_info.get('vendor', 'N/A')}"
        )
        self.info(message)
    
    def log_alert(self, alert_type: str, device_info: dict, message: str):
        log_message = (
            f"ALERT [{alert_type}] - "
            f"IP: {device_info.get('ip_address', 'N/A')}, "
            f"MAC: {device_info.get('mac_address', 'N/A')} - {message}"
        )
        self.warning(log_message)
    
    def set_level(self, level: str):
        self.logger.setLevel(getattr(logging, level))
        for handler in self.logger.handlers:
            handler.setLevel(getattr(logging, level))

logger = Logger()
