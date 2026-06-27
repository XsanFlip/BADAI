> **⚠️ DISCLAIMER / WARNING ⚠️** This tool is created **SOLELY** for educational purposes, legal penetration testing, and **Active Defense** (such as mitigating or flooding scammer bots). Any misuse of this tool for illegal activities or causing harm to others is entirely the user's responsibility.

<img width="718" height="118" alt="Screenshot From 2026-06-27 23-05-26" src="https://github.com/user-attachments/assets/cb7d8639-08f6-4998-9c17-abb968485eea" />

## 📖 Description

**B.A.D.A.I - WEB** is a Localhost Web UI interface built with Python Flask. It is designed to send payload messages to Telegram Bots or Channels/Groups asynchronously (multithreading) with precise _Rate Per Second (RPS)_ control.

**Evolution History:** Originally developed as a native Python3 Desktop/GUI application, this project has now evolved into a fully-fledged Web version. This transition provides a much more modern, mobile-responsive interface and makes remote command center access significantly easier.

Initially designed for _Active Defense_ against Telegram scammer bots, this latest _Secured_ version is equipped with advanced XSS protection, input sanitization, and security headers.

## ✨ Key Features

-   **Responsive Web UI:** A modern interface built with Tailwind CSS, 100% mobile-friendly.
    
-   **Asynchronous Engine:** Utilizes `threading` for message delivery without blocking the user interface.
    
-   **RPS Control:** Ability to throttle request speed (_Rate Per Second_) to manage API limits.
    
-   **Live Logging:** Monitor attack status (Success/Fail) in real-time directly from your browser.
    
-   **Profile Manager:** `Save` and `Load` target configurations (Token, Chat ID, Message) to a `profile.json` file to prevent repetitive typing.
    
-   **Kill-Switch Detection:** Automatically halts execution if the target bot is detected as down or banned (HTTP 401/404).
    
-   **Security Hardened:**
    
    -   Regex validation and filtering for Telegram Tokens & Chat IDs.
        
    -   `escape()` implementation to prevent HTML injection and XSS attacks.
        
    -   Strict _Content-Security-Policy (CSP)_ and _Anti-Clickjacking_ headers implemented.
        

## 🛠️ Prerequisites

Before running this script, ensure your system has the following installed:

-   [Python](https://www.python.org/downloads/ "null") version 3.8 or newer.
    
-   `pip` (Python Package Installer).
    

## 🚀 Installation (Step-by-Step)

**1. Clone this Repository**

```
git clone https://github.com/XsanFlip/BADAI.git
cd BADAI

```


**2. Create a Virtual Environment (Highly Recommended)**

```
# For Windows
python -m venv venv
venv\Scripts\activate

# For Linux / macOS
python3 -m venv venv
source venv/bin/activate

```

**3. Install Dependencies** Since this application relies on a few external libraries, install them using pip:

```
pip install Flask requests MarkupSafe

```

## 💻 Usage

**1. Run the Script** Execute the Python file in your terminal:

```
python badai-web.py

```

You should see terminal output similar to this:

```
================================================================================
🌪️ B.A.D.A.I Flask - SECURED VERSION
🕷️ Web UI - 100% Mobile Responsive
🚇 Tunnel localhost to access your command center globally
👷 c0ded by XsanLahci 2026 - Thx to Aurel666
🌐 Running on http://127.0.0.1:7326
🔒 Security Hardening Applied
================================================================================

```

**2. Access the Control Panel** Open your favorite web browser and visit the following URL: 👉 **http://127.0.0.1:7326**

**3. Configure the Attack**

-   **Bot Token Telegram:** Enter the target's Telegram Bot API token from Scammer.
    
-   **Target Chat ID:** Enter the target Chat ID, Group ID, or Channel ID from Scammer.
    
-   **Number of Messages:** Define the total number of messages to send (Max limit: 500 per session).
    
-   **Rate Per Second (RPS):** Set the delivery speed (Recommended: 10 - 30 RPS to avoid hitting Telegram API rate limits too quickly).
    
-   **Payload Message:** Write the message payload you wish to send (Supports Telegram's default HTML formatting).
    

**4. Start / Stop Execution**

-   Click **🚀 START** to begin the execution.
    
-   Click **🛑 STOP** to manually force stop the process at any time.
    
-   Use the **💾 Save Profile** button to store your configuration for future use.
    

## 🛡️ Security & Network Notes

-   **Localhost Only:** By default, this application binds to `host='127.0.0.1'`. This means the application can only be accessed from your local machine, preventing unauthorized access from your local network.
    
-   **Remote Access:** If you install this on a VPS and wish to access the UI remotely, it is highly recommended to use _Tunneling_ (such as `ngrok`, `Cloudflare Tunnels`, or `SSH port forwarding`) rather than changing the host to `0.0.0.0`.
    

## 👨‍💻 Author & Credits

-   **Author:** xsanlahci © 2026
    
-   **Special Thanks to:** Aurel666
    

_If you find this tool helpful for your active defense research, don't forget to give a ⭐ on this repository!_
