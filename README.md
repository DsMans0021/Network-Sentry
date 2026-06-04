# Network Sentry
![Application Icon](icon.png)

A tool that helps you keep an eye on everything connected to your network. Network Sentry discovers devices, tracks them, and alerts you when something new shows up. It's designed to be easy to use, even if you're not a networking expert.

## Download from here: https://raw.githubusercontent.com/DsMans0021/Network-Sentry/main/released%20v1.0/NetworkSentry.exe

## What Can It Do?

- Find devices on your network automatically
- Keep a record of which devices have connected to your network
- Identify what brand made each device
- Get alerts when new devices appear
- Check your network regularly without manual work
- Save device info as reports (CSV or JSON)
- Works on Windows, Mac, and Linux

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

## Getting Started

### What You Need

- Python 3.8 or newer
- Admin or root access on your computer (needed to scan the network)

### Installation

1. Download or clone the project and go into the folder:
```bash
cd network_sentry
```

2. Install what the app needs:
```bash
pip install -r requirements.txt
```

3. Run the app (you'll need admin rights):
```bash
# On Mac or Linux
sudo python main.py

# On Windows (run Command Prompt as Administrator)
python main.py
```

## Tutorial

Watch the YouTube tutorial for a detailed walkthrough:
[Network Sentry YouTube Tutorial](https://youtu.be/3NvYwcGC570)

## Screenshots

![Network Sentry](Network%20Sentry.png)

## Usage

## How to Use It

When you start the app, you'll see a simple menu with these options:

1. **Scan Network Now** - Look for devices right now
2. **View All Devices** - See everything you've found
3. **View Unknown Devices** - See new devices you haven't marked as safe
4. **Mark Device as Known** - Tell the app a device is supposed to be there
5. **Start Continuous Monitoring** - Let it check for new devices automatically
6. **View Alert History** - See past notifications
7. **Export Report** - Save your device list as a file
8. **Settings** - Change how alerts work
9. **Exit** - Close the app

Just number what you want to do and press Enter.

## Settings

You can change how the app works by editing `config.py`:

- **Database**: Where device info is stored (`network_sentry.db`)
- **Scan Interval**: How often to check (default: 5 minutes)
- **Log File**: Where activity is recorded (`network_sentry.log`)
- **Max Threads**: Controls speed (default: 50)
- **Alerts**: Customize what kind of alerts you get

## Alert Types

- **NEW_DEVICE**: A device you haven't seen before is on your network
- **KNOWN_DEVICE_RETURNED**: A device you marked as safe is back
- **SUSPICIOUS_ACTIVITY**: Something unusual happened on your network

## How Data is Organized

### Devices
The app stores this info about each device:
- IP address (the device's network ID)
- MAC address (the device's hardware ID)
- Hostname (device name if available)
- When you first saw it
- When you last saw it
- If it's marked as safe
- What brand/manufacturer it is

### Alerts
Each alert is recorded with:
- Which device triggered it
- What kind of alert it is
- Custom message
- When it happened

## Important Info

- **You Need Admin Access**: Requires special permissions to scan networks
- **Legal Use Only**: Only use this to monitor networks you own or have permission to monitor
- **Safe Scanning**: This tool just looks, it doesn't mess with the network
- **Passive**: Uses listening-only methods, no intrusive scanning

## Having Problems?

### I get permission errors
- Mac/Linux: Make sure you use `sudo` when running the app
- Windows: Run the Command Prompt as Administrator
- Check your firewall isn't blocking the app

### No devices are showing up
- Double-check your network setup
- Make sure you're on the right network
- Check that devices are actually plugged in and turned on

### Import errors or missing packages
- Run this command again: `pip install -r requirements.txt`
- Make sure you're using Python 3.8 or newer

## What Powers Network Sentry

- `scapy` - Tools for working with network packets
- `python-nmap` - Finding devices on networks
- `colorama` - Colors in the terminal
- `netifaces` - Reads network info
- `tabulate` - Makes nice tables to display info
- `mac-vendor-lookup` - Looks up device brands

## License

This project is for learning and monitoring your own network. Please use it responsibly.

## Sharing Improvements

Found a bug or want to add features? We'd love your help! Just make sure:
- Your code is clean and easy to follow
- Functions have comments explaining what they do
- You handle errors properly
- Test it on different operating systems

## Warning

Use Network Sentry only on networks you own or have permission to monitor. Scanning someone else's network without permission might be illegal where you live. Be responsible with this tool.

## Whoami
>_Made With ❤️ by DsMans0021
