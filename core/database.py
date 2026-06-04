
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import Config

class DatabaseManager:
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_path = Config.get_db_path()
            self._local = threading.local()
            self._initialize_database()
            self.initialized = True
    
    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    def _initialize_database(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT UNIQUE NOT NULL,
            mac_address TEXT NOT NULL,
            hostname TEXT,
            vendor TEXT,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            is_known INTEGER DEFAULT 0
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            alert_type TEXT NOT NULL,
            message TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        )''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mac ON devices(mac_address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip ON devices(ip_address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_known ON devices(is_known)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
        
        conn.commit()
    
    def add_device(self, ip: str, mac: str, hostname: str = None, vendor: str = None) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            cursor.execute('''INSERT INTO devices (ip_address, mac_address, hostname, vendor, first_seen, last_seen, is_known)
                            VALUES (?, ?, ?, ?, ?, ?, 0)''',
                          (ip, mac, hostname, vendor, timestamp, timestamp))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return self.update_device(ip, mac, hostname, vendor)
    
    def update_device(self, ip: str, mac: str = None, hostname: str = None, vendor: str = None) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        updates = ['last_seen = ?']
        params = [timestamp]
        
        if mac:
            updates.append('mac_address = ?')
            params.append(mac)
        if hostname:
            updates.append('hostname = ?')
            params.append(hostname)
        if vendor:
            updates.append('vendor = ?')
            params.append(vendor)
        
        params.append(ip)
        
        update_query = f"UPDATE devices SET {', '.join(updates)} WHERE ip_address = ?"
        cursor.execute(update_query, params)
        conn.commit()
        
        cursor.execute('SELECT id FROM devices WHERE ip_address = ?', (ip,))
        row = cursor.fetchone()
        return row['id'] if row else None
    
    def get_all_devices(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM devices')
        devices = []
        for row in cursor.fetchall():
            devices.append({
                'id': row['id'],
                'ip_address': row['ip_address'],
                'mac_address': row['mac_address'],
                'hostname': row['hostname'],
                'first_seen': row['first_seen'],
                'last_seen': row['last_seen'],
                'is_known': bool(row['is_known']),
                'vendor': row['vendor']
            })
        
        return devices
    
    def get_unknown_devices(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM devices WHERE is_known = 0')
        devices = []
        for row in cursor.fetchall():
            devices.append({
                'id': row['id'],
                'ip_address': row['ip_address'],
                'mac_address': row['mac_address'],
                'hostname': row['hostname'],
                'first_seen': row['first_seen'],
                'last_seen': row['last_seen'],
                'is_known': bool(row['is_known']),
                'vendor': row['vendor']
            })
        
        return devices
    
    def mark_as_known(self, mac_address: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE devices SET is_known = 1 WHERE mac_address = ?', (mac_address,))
        conn.commit()
        return cursor.rowcount > 0
    
    def get_device_by_mac(self, mac_address: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM devices WHERE mac_address = ?', (mac_address,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'ip_address': row['ip_address'],
                'mac_address': row['mac_address'],
                'hostname': row['hostname'],
                'first_seen': row['first_seen'],
                'last_seen': row['last_seen'],
                'is_known': bool(row['is_known']),
                'vendor': row['vendor']
            }
        return None
    
    def delete_device(self, ip: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM devices WHERE ip_address = ?', (ip,))
        conn.commit()
        return cursor.rowcount > 0
    
    def get_device_stats(self) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM devices')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as known FROM devices WHERE is_known = 1')
        known = cursor.fetchone()['known']
        
        cursor.execute('SELECT COUNT(*) as unknown FROM devices WHERE is_known = 0')
        unknown = cursor.fetchone()['unknown']
        
        return {
            'total': total,
            'known': known,
            'unknown': unknown
        }
    
    def add_alert(self, device_id: int, alert_type: str, message: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''INSERT INTO alerts (device_id, alert_type, message, timestamp)
                         VALUES (?, ?, ?, ?)''',
                      (device_id, alert_type, message, timestamp))
        conn.commit()
        return cursor.lastrowid
    
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT a.id, a.alert_type, a.message, a.timestamp,
                                 d.ip_address, d.mac_address, d.hostname
                          FROM alerts a
                          LEFT JOIN devices d ON a.device_id = d.id
                          ORDER BY a.timestamp DESC
                          LIMIT ?''', (limit,))
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row['id'],
                'alert_type': row['alert_type'],
                'message': row['message'],
                'timestamp': row['timestamp'],
                'ip_address': row['ip_address'],
                'mac_address': row['mac_address'],
                'hostname': row['hostname']
            })
        
        return alerts
    
    def cleanup_old_devices(self, days: int = 30) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''DELETE FROM devices 
                         WHERE last_seen < datetime('now', '-' || ? || ' days')''', (days,))
        conn.commit()
        return cursor.rowcount
    
    def close(self):
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
