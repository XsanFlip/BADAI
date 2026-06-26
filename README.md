
# B.A.D.A.I 🌪️

**Bot Attack & Defense Asynchronous Interface**

<img width="500" height="500" alt="logo-badai" src="https://github.com/user-attachments/assets/53063d8b-81f8-494f-81ef-73c69d620747" />


> Developed by **xsanlahci** | _Active Defense Tool against Phishing/Scam Bots_

B.A.D.A.I is a modern, Python-based GUI application designed for Load Testing or launching retaliatory attacks (_Active Defense_) against scam/phishing Telegram bots. Utilizing a high-level asynchronous architecture (`asyncio` & `aiohttp`), this application is capable of sending up to 50+ messages per second (RPS) to flood and paralyze a threat actor's Telegram bot database.

## ✨ Key Features

-   **🚀 Asynchronous Engine**: Capable of sending dozens of messages per second in parallel without blocking the application interface.
    
-   **🎨 Modern & Responsive UI**: Built with `CustomTkinter`, featuring Dark Mode support, a Progress Bar, and a borderless splash screen interface.
    
-   **🎯 Smart Kill-Switch**: Automatically detects if the target bot has been taken down or banned (Error 401/404) and immediately halts the attack with visual/audio notifications.
    
-   **💾 Profile Manager**: Save & Load functionality for Token, Chat ID, and Payload configurations into a `profile.json` file so you don't have to retype them every time.
    
-   **🛡️ Auto-Throttle & Anti-Ban**: Smart handling of _Error 429 (Too Many Requests)_ from the Telegram API to maintain the attack persistence without getting network-banned.
    
-   **📈 Real-time Live Logging**: Smooth status monitoring (Success/Failed/Target) running seamlessly thanks to its multithreading architecture.
    

## 🛠️ System Requirements

-   Python 3.7 or newer
    
-   Operating System: Windows / Linux / macOS
    
-   Stable internet connection
    

## 🚀 Installation & Setup Guide

It is highly recommended to use a _Virtual Environment_ (venv) to prevent library conflicts with your other Python projects.

### Step 1: Clone / Prepare Folder

Open your terminal and navigate to this project folder. Ensure `telegram_spammer.py` and `logo.png` (optional) are in the same directory.

### Step 2: Create a Virtual Environment

```
python3 -m venv venv

```

### Step 3: Activate the Virtual Environment

**For Linux / macOS:**

```
source venv/bin/activate

```

**For Windows:**

```
venv\Scripts\activate

```

_(Indicator that it is active: you will see `(venv)` at the beginning of your terminal prompt)._

### Step 4: Install Dependencies

Install all required third-party libraries (`aiohttp`, `customtkinter`, `pillow`) using:

```
pip install aiohttp customtkinter pillow

```

### Step 5: Run B.A.D.A.I

```
python telegram_spammer.py

```

## 📖 How to Use (UI)

<img width="704" height="765" alt="Screenshot_2026-06-26_16-13-28" src="https://github.com/user-attachments/assets/d1fb8db9-43fa-4e0f-9d57-ea597b7a8581" />


1.  **API Configuration**:
    
    -   Enter the target's **Bot Token** (obtained from your Threat Intel / intercepted web traffic).
        
    -   Enter the **Target Chat ID** (Private Chat, Channel, or Group where the scammer receives the stolen data).
        
2.  **Payload Message**: Enter the fake data / dummy credentials you want to send. This text supports Telegram HTML formatting (e.g., `<b>Credit Card:</b> 1234...`).
    
3.  **Attack Config**:
    
    -   Set the **Message Count** (e.g., `5000`).
        
    -   Set the **Speed (RPS)** (recommended: `30` - `50`).
        
4.  _(Optional)_ Click **💾 Save Profile** to easily load your configuration later.
    
5.  Click **🚀 START SENDING** and watch the scammer's database get flooded with noise!
    

## ⚠️ Legal Warning (Disclaimer)

-   This tool is created **STRICTLY** for educational purposes, legal penetration testing, and **Active Defense** against cyber threats (such as phishing/scam syndicates).
    
-   **Telegram Rate Limits**: The Telegram API has global rate limits. Do not abuse this tool to spam innocent parties, groups, or individuals.
    
-   Any misuse of this tool is **entirely the user's responsibility**. The author (**xsanlahci**) is exempt from any legal action or liability arising from the illegal or malicious use of this tool.
