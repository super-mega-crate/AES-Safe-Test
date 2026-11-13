# 🛡️ SystemLocker: Ransomware Simulation & Security Research Tool

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green)
![Cryptography](https://img.shields.io/badge/Cryptography-AES--256-red)
![Status](https://img.shields.io/badge/Status-Educational_Use_Only-orange)

> **⚠️ DISCLAIMER:** This project is developed **strictly for educational and security research purposes**. It is designed to demonstrate how ransomware operates, how it interacts with the Windows Registry, and how encryption works. The author is not responsible for any misuse or damage caused by this software. **DO NOT RUN THIS ON A REAL PC WITHOUT A BACKUP. USE A VIRTUAL MACHINE.**

---

## 📖 About The Project

**SystemLocker** is a Proof of Concept (PoC) designed to simulate the behavior of modern ransomware. It was built to help cybersecurity enthusiasts and Junior Penetration Testers understand the mechanics of a cyberattack from the inside. 

Instead of just being a "scary prank," this project features a modular enterprise-level architecture, a built-in emergency backup system, and real-time Telegram notifications.

### 🚀 Key Features

*   **AES-256 Encryption:** Uses `cryptography.fernet` to securely encrypt files.
*   **Emergency Backup:** Before encrypting anything, the tool automatically creates a ZIP archive of the target directory to prevent permanent data loss.
*   **Process Masquerading:** Hides itself in `%APPDATA%` and renames the executable to `svchost.exe` to blend in with system processes.
*   **System Policy Modification:** Uses `HKLM` registry keys to disable Task Manager, Registry Editor, and CMD (requires Administrator privileges).
*   **Telegram Integration:** Sends real-time alerts to the attacker (or researcher) when the locker is deployed and when the password is entered.
*   **Anti-Kill Protection:** Blocks `taskkill.exe` and prevents system shutdown while active.
*   **Modular Architecture:** Clean separation of concerns (UI, Crypto, System Tools, Notifications).

---

## 📂 Project Structure

The project follows a modern, modular architecture:

```text
SystemLocker/
├── config.json          # Configuration (Password, Telegram token, etc.)
├── main.py              # Entry point
├── logo.png             # UI Logo
├── core/
│   ├── __init__.py
│   ├── crypto.py        # Encryption & Backup logic
│   ├── sys_tools.py     # Registry & Process hiding
│   ├── telegram.py      # Telegram API notifications
│   └── ui.py            # PyQt6 Interface & Matrix animation
⚙️ Installation & Usage
1. Prerequisites
Python 3.10+

Windows OS (requires Administrator privileges)

Dependencies:

bash
pip install PyQt6 cryptography requests keyboard
2. Configuration
Open config.json and set your parameters:

json
{
  "app_name": "Windows Security Health Service",
  "password": "your_super_secret_password",
  "telegram_token": "YOUR_BOT_TOKEN",
  "telegram_chat_id": "YOUR_CHAT_ID",
  "target_dir": "Desktop",
  "timer_hours": 48
}
3. Running the Simulation
WARNING: Test this only in a Virtual Machine (VirtualBox/VMware) or on a sandboxed PC.

bash
python main.py
4. Building to EXE
To compile the project into a standalone executable:

bash
pyinstaller --noconsole --onefile --collect-all PyQt6 --collect-all cryptography --add-data "core;core" --add-data "config.json;." --add-data "logo.png;." main.py
🛡️ How to Defend Against This (Blue Team Notes)
This tool highlights several Windows vulnerabilities:

Registry Policies: Users with Admin rights can always revert HKLM changes.

Safe Mode: Booting into Safe Mode bypasses the autostart and registry policies, allowing users to remove the malware.

Backups: The built-in emergency backup (emergency_backup.zip in AppData/WindowsCache) demonstrates why offline backups are critical against real ransomware.

⚖️ License & Legal
This project is licensed under the MIT License.

By using this software, you agree that you are solely responsible for your actions. The creator of this repository does not condone or support cybercrime, extortion, or any illegal activities. This is a purely academic project created to learn how malware works so we can better defend against it.
