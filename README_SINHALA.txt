SUPER RED CYBER TERMINAL V∞ — NO AI
=====================================

WINDOWS 10 SETUP (සිංහල)

1. ZIP file එක Extract All කරන්න.
2. Extract කළ folder එක open කරන්න.
3. File Explorer address bar එක click කරලා cmd කියලා type කර Enter කරන්න.
4. මේ command එක run කරන්න:
       python main.py
5. App එක open වෙයි.

මෙම app එක Python standard library සහ Tkinter භාවිතා කරයි.
අමතර pip package install කිරීම අවශ්‍ය නැහැ.

EXE හදන විදිහ
--------------
1. Command Prompt එකේ project folder එකේ ඉන්න.
2. Run:
       python -m pip install pyinstaller
3. ඉන්පසු:
       python -m PyInstaller --onefile --windowed --name SUPER_RED_CYBER_TERMINAL main.py
4. EXE එක මෙතැනින් ලැබේ:
       dist\SUPER_RED_CYBER_TERMINAL.exe

FEATURES
--------
- Dashboard: PC and local IP details
- Network: Windows ARP cache viewer (passive)
- Ports: common TCP ports on 127.0.0.1 only
- Wi-Fi/IP: ipconfig and netsh Wi-Fi details
- DNS: hostname lookup
- Website: HTTPS response security headers
- Password: local strength check; does not save or transmit the password
- File Integrity: SHA-256 fingerprint of a selected file
- Processes: read-only process list
- Reports: local text reports and activity log

SAFETY
------
Use only on your own PC, your own network, and websites/systems where you have explicit permission.
The port checker is intentionally limited to this PC (127.0.0.1).
The network page reads the existing ARP cache; it does not perform an aggressive network sweep.
The website inspector only accepts HTTPS URLs and checks response headers. It is not an exploit tool.
The password auditor does not store or transmit the entered sample password.

If Python is not recognized, install Python from python.org and enable
"Add Python to PATH" during installation.
