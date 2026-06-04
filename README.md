# Network Sentry

A comprehensive Network Monitoring and Security Scanning Tool for network administrators and cybersecurity enthusiasts. Network Sentry provides real-time device discovery, tracking, and alerting through an intuitive CLI interface.

## Features

- **Network Scanning**: ARP-based device discovery with concurrent scanning for speed
- **Device Tracking**: Persistent storage of discovered devices with connection history
- **Vendor Identification**: Automatic manufacturer lookup from MAC addresses using OUI database
- **Alert System**: Real-time notifications for new devices and network events
- **Continuous Monitoring**: Automated scanning at configurable intervals
- **Reporting**: Export device data to CSV or JSON formats
- **Cross-Platform**: Works on Windows, Linux, and macOS

## Project Structure

```
network_sentry/
├── main.py                 # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── core/
│   ├── __init__.py
│   ├── scanner.py        # Network scanning functionality
│   ├── database.py       # Database operations
│   └── alert_system.py   # Alert management
└── utils/
    ├── __init__.py
    ├── logger.py         # Logging utilities
    └── helpers.py        # Helper functions
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Administrator/root privileges (required for raw socket operations)

### Setup

1. Clone or download the project:
```bash
cd network_sentry
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application (requires admin/root):
```bash
# On Linux/macOS
sudo python main.py

# On Windows (run as Administrator)
python main.py
```

## Usage

### Main Menu

Network Sentry provides an interactive CLI with the following options:

1. **Scan Network Now** - Perform an immediate network scan
2. **View All Devices** - Display all devices in the database
3. **View Unknown Devices** - Show devices not marked as known
4. **Mark Device as Known** - Mark a device as trusted
5. **Start Continuous Monitoring** - Enable automated scanning
6. **View Alert History** - Review past alerts
7. **Export Report** - Export data to CSV or JSON
8. **Settings** - Configure alert preferences
9. **Exit** - Close the application

### Example Usage

```bash
$ sudo python main.py

╔════════════════════════════════════════════════════════════╗
║                                                              ║
║                    NETWORK SENTRY                            ║
║              Network Monitoring & Security Tool              ║
║                                                              ║
║           Monitoring Your Network 24/7                      ║
║                                                              ║
╚════════════════════════════════════════════════════════════╝

Main Menu
==================================================
1. Scan Network Now
2. View All Devices
3. View Unknown Devices
4. Mark Device as Known
5. Start Continuous Monitoring
6. View Alert History
7. Export Report (CSV/JSON)
8. Settings
9. Exit
==================================================

Enter your choice (1-9): 1

[*] Network Scan
==================================================

[*] Scanning network: 192.168.1.0/24
[*] This may take a moment...

[+] Found 5 device(s):

+--------------+-------------------+----------------+----------------+
| IP Address   | MAC Address       | Hostname       | Vendor         |
+--------------+-------------------+----------------+----------------+
| 192.168.1.1  | AA:BB:CC:DD:EE:FF | router.local   | Cisco Systems  |
| 192.168.1.100| 11:22:33:44:55:66 | laptop-john    | Apple Inc.     |
+--------------+-------------------+----------------+----------------+
```

## Configuration

Configuration settings are stored in `config.py`:

- **Database Path**: `network_sentry.db` (SQLite)
- **Scan Interval**: 300 seconds (5 minutes)
- **Log File**: `network_sentry.log`
- **Max Threads**: 50 (for concurrent scanning)
- **Alert Settings**: Configurable via Settings menu

## Alert Types

- **NEW_DEVICE**: Unknown device detected on the network (Red)
- **KNOWN_DEVICE_RETURNED**: Known device reconnected (Green)
- **SUSPICIOUS_ACTIVITY**: Potential security anomaly (Yellow)

## Database Schema

### Devices Table
- `id` - Primary key
- `ip_address` - Device IP address (unique)
- `mac_address` - Device MAC address
- `hostname` - Resolved hostname
- `first_seen` - First detection timestamp
- `last_seen` - Last detection timestamp
- `is_known` - Known device flag
- `vendor` - Device manufacturer

### Alerts Table
- `id` - Primary key
- `device_id` - Foreign key to devices
- `alert_type` - Type of alert
- `message` - Alert message
- `timestamp` - Alert timestamp

## Security Considerations

- **Permissions**: Requires administrator/root privileges for raw socket operations
- **Educational Use**: Intended for authorized network monitoring only
- **Privacy**: Respects network privacy; no malicious packet injection
- **Passive Mode**: ARP scanning is passive and non-intrusive

## Troubleshooting

### Permission Denied Errors
- Run with sudo on Linux/macOS
- Run as Administrator on Windows
- Ensure firewall allows the application

### No Devices Found
- Check network interface configuration
- Verify you're on the correct network
- Ensure devices are powered on and connected

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

## Dependencies

- `scapy` - Packet manipulation and network scanning
- `python-nmap` - Network discovery
- `colorama` - Cross-platform colored terminal text
- `netifaces` - Network interface enumeration
- `tabulate` - Pretty-print tabular data
- `mac-vendor-lookup` - MAC address OUI lookup

## License

This project is provided for educational and authorized network monitoring purposes only.

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- All functions have docstrings
- Error handling is comprehensive
- Changes are tested on multiple platforms

## Disclaimer

Network Sentry is intended for legitimate network monitoring and security auditing on networks you own or have explicit permission to monitor. Unauthorized network scanning may be illegal in your jurisdiction. Use responsibly.

## Whoami
>_Made With ❤️ by DsMans0021
