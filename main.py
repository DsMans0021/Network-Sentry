import sys
import time
import signal
from pathlib import Path
from typing import Optional
from colorama import Fore, Style, init

sys.path.append(str(Path(__file__).parent))

from config import Config
from core.database import DatabaseManager
from core.scanner import NetworkScanner
from core.alert_system import AlertSystem
from utils.logger import logger
from utils.helpers import (
    clear_screen,
    print_banner,
    validate_ip,
    get_current_timestamp,
    calculate_network_range
)
from tabulate import tabulate

init(autoreset=True)

menu = f"""
{Fore.CYAN}======================================{Style.RESET_ALL}
{Fore.CYAN}      Network Sentry - Main Menu      {Style.RESET_ALL}
{Fore.CYAN}======================================{Style.RESET_ALL}

{Fore.GREEN}1. Run Network Scan{Style.RESET_ALL}
{Fore.GREEN}2. View All Devices{Style.RESET_ALL}
{Fore.GREEN}3. View Unknown Devices{Style.RESET_ALL}
{Fore.GREEN}4. Mark Device as Known{Style.RESET_ALL}
{Fore.GREEN}5. Continuous Monitoring{Style.RESET_ALL}
{Fore.GREEN}6. View Alert History{Style.RESET_ALL}
{Fore.GREEN}7. Export Report{Style.RESET_ALL}
{Fore.GREEN}8. Settings{Style.RESET_ALL}
{Fore.RED}9. Exit{Style.RESET_ALL}
"""

class NetworkSentryApp:
    
    def __init__(self):
        self.db = DatabaseManager()
        self.scanner = NetworkScanner()
        self.alert_system = AlertSystem()
        self.running = True
        self.monitoring = False
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        print(f"\n{Fore.YELLOW}[*] Shutting down gracefully...{Style.RESET_ALL}")
        self.running = False
        self.monitoring = False
        self.scanner.stop_scan()
        sys.exit(0)
    
    def run(self):
        while self.running:
            clear_screen()
            print_banner()
            self._print_menu()
            
            try:
                choice = input(f"\n{Fore.CYAN}Enter your choice (1-9): {Style.RESET_ALL}").strip()
                self._handle_menu_choice(choice)
            except KeyboardInterrupt:
                self._signal_handler(signal.SIGINT, None)
            except Exception as e:
                print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
                logger.error(f"Menu choice error: {e}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def _print_menu(self):
        print(menu)
    
    def _handle_menu_choice(self, choice: str):
        if choice == '1':
            self.run_scan()
        elif choice == '2':
            self.view_all_devices()
        elif choice == '3':
            self.view_unknown_devices()
        elif choice == '4':
            self.mark_device_known()
        elif choice == '5':
            self.continuous_monitor()
        elif choice == '6':
            self.view_alert_history()
        elif choice == '7':
            self.export_report()
        elif choice == '8':
            self.settings_menu()
        elif choice == '9':
            print(f"{Fore.GREEN}[*] Goodbye!{Style.RESET_ALL}")
            self.running = False
        else:
            print(f"{Fore.RED}[!] Invalid choice. Please try again.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def run_scan(self):
        print(f"\n{Fore.YELLOW}[*] Network Scan{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        
        network_range = self.scanner.get_network_range()
        print(f"{Fore.CYAN}[*] Scanning network: {network_range}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] This may take a moment...{Style.RESET_ALL}\n")
        
        devices = self.scanner.scan_network(network_range)
        
        if not devices:
            print(f"{Fore.YELLOW}[!] No devices found.{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[+] Found {len(devices)} device(s):{Style.RESET_ALL}\n")
            
            self._display_devices(devices)
            
            print(f"\n{Fore.YELLOW}[*] Saving devices to database...{Style.RESET_ALL}")
            for device in devices:
                self.db.add_device(
                    device['ip'],
                    device['mac'],
                    device['hostname'],
                    device['vendor']
                )
            
            self.alert_system.process_scan_results(devices)
            
            print(f"{Fore.GREEN}[+] Scan complete!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def view_all_devices(self):
        print(f"\n{Fore.YELLOW}[*] All Devices{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        
        devices = self.db.get_all_devices()
        stats = self.db.get_device_stats()
        
        print(f"{Fore.CYAN}Statistics: {stats['total']} total, {stats['known']} known, {stats['unknown']} unknown{Style.RESET_ALL}\n")
        
        if not devices:
            print(f"{Fore.YELLOW}[!] No devices in database.{Style.RESET_ALL}")
        else:
            self._display_db_devices(devices)
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def view_unknown_devices(self):
        print(f"\n{Fore.YELLOW}[*] Unknown Devices{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        
        devices = self.db.get_unknown_devices()
        
        if not devices:
            print(f"{Fore.GREEN}[+] No unknown devices found.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[!] Found {len(devices)} unknown device(s):{Style.RESET_ALL}\n")
            self._display_db_devices(devices)
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def mark_device_known(self):
        print(f"\n{Fore.YELLOW}[*] Mark Device as Known{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        
        unknown_devices = self.db.get_unknown_devices()
        
        if not unknown_devices:
            print(f"{Fore.GREEN}[+] No unknown devices to mark.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        self._display_db_devices(unknown_devices)
        
        print(f"\n{Fore.CYAN}Enter the MAC address of the device to mark as known:{Style.RESET_ALL}")
        mac = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
        
        if self.db.mark_as_known(mac):
            print(f"{Fore.GREEN}[+] Device marked as known.{Style.RESET_ALL}")
            logger.info(f"Device {mac} marked as known")
        else:
            print(f"{Fore.RED}[!] Failed to mark device. Check MAC address.{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def continuous_monitor(self):
        print(f"\n{Fore.YELLOW}[*] Continuous Monitoring{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        
        network_range = self.scanner.get_network_range()
        interval = Config.SCAN_INTERVAL
        
        print(f"{Fore.CYAN}[*] Monitoring network: {network_range}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Scan interval: {interval} seconds{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Press Ctrl+C to stop monitoring{Style.RESET_ALL}\n")
        
        self.monitoring = True
        
        try:
            while self.monitoring and self.running:
                timestamp = get_current_timestamp()
                print(f"{Fore.CYAN}[{timestamp}] Starting scan...{Style.RESET_ALL}")
                
                devices = self.scanner.scan_network(network_range)
                
                if devices:
                    print(f"{Fore.GREEN}[+] Found {len(devices)} device(s){Style.RESET_ALL}")
                    
                    for device in devices:
                        self.db.add_device(
                            device['ip'],
                            device['mac'],
                            device['hostname'],
                            device['vendor']
                        )
                    
                    self.alert_system.monitor_devices(devices)
                else:
                    print(f"{Fore.YELLOW}[!] No devices found{Style.RESET_ALL}")
                
                print(f"{Fore.CYAN}[*] Next scan in {interval} seconds...{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}\n")
                
                for _ in range(interval):
                    if not self.monitoring or not self.running:
                        break
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Monitoring stopped.{Style.RESET_ALL}")
        
        self.monitoring = False
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def view_alert_history(self):
        print(f"\n{Fore.YELLOW}[*] Alert History{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        
        alerts = self.alert_system.get_alert_history(limit=50)
        self.alert_system.print_alert_summary(alerts)
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def export_report(self):
        print(f"\n{Fore.YELLOW}[*] Export Report{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}Select format:{Style.RESET_ALL}")
        print(f"1. CSV")
        print(f"2. JSON")
        
        choice = input(f"\n{Fore.CYAN}> {Style.RESET_ALL}").strip()
        
        devices = self.db.get_all_devices()
        
        if not devices:
            print(f"{Fore.YELLOW}[!] No devices to export.{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        export_dir = Config.get_export_dir()
        timestamp = get_current_timestamp().replace(' ', '_').replace(':', '-')
        
        if choice == '1':
            filename = export_dir / f"network_report_{timestamp}.csv"
            self._export_csv(devices, filename)
        elif choice == '2':
            filename = export_dir / f"network_report_{timestamp}.json"
            self._export_json(devices, filename)
        else:
            print(f"{Fore.RED}[!] Invalid choice.{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def _export_csv(self, devices: list, filename: Path):
        import csv
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['ip_address', 'mac_address', 'hostname', 'vendor', 'first_seen', 'last_seen', 'is_known']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for device in devices:
                    writer.writerow({
                        'ip_address': device['ip_address'],
                        'mac_address': device['mac_address'],
                        'hostname': device['hostname'],
                        'vendor': device['vendor'],
                        'first_seen': device['first_seen'],
                        'last_seen': device['last_seen'],
                        'is_known': device['is_known']
                    })
            
            print(f"{Fore.GREEN}[+] Report exported to: {filename}{Style.RESET_ALL}")
            logger.info(f"Report exported to {filename}")
        except Exception as e:
            print(f"{Fore.RED}[!] Export failed: {e}{Style.RESET_ALL}")
            logger.error(f"CSV export error: {e}")
    
    def _export_json(self, devices: list, filename: Path):
        import json
        
        try:
            report = {
                'timestamp': get_current_timestamp(),
                'total_devices': len(devices),
                'devices': devices
            }
            
            with open(filename, 'w') as jsonfile:
                json.dump(report, jsonfile, indent=2, default=str)
            
            print(f"{Fore.GREEN}[+] Report exported to: {filename}{Style.RESET_ALL}")
            logger.info(f"Report exported to {filename}")
        except Exception as e:
            print(f"{Fore.RED}[!] Export failed: {e}{Style.RESET_ALL}")
            logger.error(f"JSON export error: {e}")
    
    def settings_menu(self):
        while True:
            print(f"\n{Fore.YELLOW}[*] Settings{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
            
            alert_settings = self.alert_system.get_alert_settings()
            
            print(f"{Fore.CYAN}Alert Settings:{Style.RESET_ALL}")
            print(f"1. New Device Alerts: {'Enabled' if alert_settings['new_device'] else 'Disabled'}")
            print(f"2. Known Device Returned Alerts: {'Enabled' if alert_settings['known_device_returned'] else 'Disabled'}")
            print(f"3. Suspicious Activity Alerts: {'Enabled' if alert_settings['suspicious_activity'] else 'Disabled'}")
            print(f"4. Back to Main Menu")
            
            choice = input(f"\n{Fore.CYAN}> {Style.RESET_ALL}").strip()
            
            if choice == '1':
                self._toggle_alert(AlertSystem.NEW_DEVICE)
            elif choice == '2':
                self._toggle_alert(AlertSystem.KNOWN_DEVICE_RETURNED)
            elif choice == '3':
                self._toggle_alert(AlertSystem.SUSPICIOUS_ACTIVITY)
            elif choice == '4':
                break
            else:
                print(f"{Fore.RED}[!] Invalid choice.{Style.RESET_ALL}")
    
    def _toggle_alert(self, alert_type: str):
        settings = self.alert_system.get_alert_settings()
        
        if alert_type == AlertSystem.NEW_DEVICE:
            current = settings['new_device']
            if current:
                self.alert_system.disable_alert(alert_type)
                print(f"{Fore.YELLOW}[!] New device alerts disabled.{Style.RESET_ALL}")
            else:
                self.alert_system.enable_alert(alert_type)
                print(f"{Fore.GREEN}[+] New device alerts enabled.{Style.RESET_ALL}")
        elif alert_type == AlertSystem.KNOWN_DEVICE_RETURNED:
            current = settings['known_device_returned']
            if current:
                self.alert_system.disable_alert(alert_type)
                print(f"{Fore.YELLOW}[!] Known device returned alerts disabled.{Style.RESET_ALL}")
            else:
                self.alert_system.enable_alert(alert_type)
                print(f"{Fore.GREEN}[+] Known device returned alerts enabled.{Style.RESET_ALL}")
        elif alert_type == AlertSystem.SUSPICIOUS_ACTIVITY:
            current = settings['suspicious_activity']
            if current:
                self.alert_system.disable_alert(alert_type)
                print(f"{Fore.YELLOW}[!] Suspicious activity alerts disabled.{Style.RESET_ALL}")
            else:
                self.alert_system.enable_alert(alert_type)
                print(f"{Fore.GREEN}[+] Suspicious activity alerts enabled.{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def _display_devices(self, devices: list):
        table_data = []
        for device in devices:
            known_status = f"{Fore.GREEN}Known{Style.RESET_ALL}" if device.get('known') else f"{Fore.RED}Unknown{Style.RESET_ALL}"
            table_data.append([
                device.get('ip', 'N/A'),
                device.get('mac', 'N/A'),
                device.get('hostname', 'N/A'),
                device.get('vendor', 'N/A')
            ])
        
        headers = ['IP Address', 'MAC Address', 'Hostname', 'Vendor']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    def _display_db_devices(self, devices: list):
        table_data = []
        for device in devices:
            known_status = f"{Fore.GREEN}Yes{Style.RESET_ALL}" if device['is_known'] else f"{Fore.RED}No{Style.RESET_ALL}"
            table_data.append([
                device['ip_address'],
                device['mac_address'],
                device['hostname'] or 'N/A',
                device['vendor'] or 'N/A',
                known_status,
                device['last_seen']
            ])
        
        headers = ['IP', 'MAC', 'Hostname', 'Vendor', 'Known', 'Last Seen']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))

def main():
    try:
        app = NetworkSentryApp()
        app.run()
    except Exception as e:
        print(f"{Fore.RED}[!] Fatal error: {e}{Style.RESET_ALL}")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
