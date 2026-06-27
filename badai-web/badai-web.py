from flask import Flask, render_template_string, request, jsonify, abort
import threading
import time
import json
import os
from datetime import datetime
from markupsafe import escape
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)  # Random secret key setiap start
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # Maks 1MB

is_running = False
success_count = 0
fail_count = 0
total_count = 0
stop_flag = False
logs = []

PROFILE_FILE = 'profile.json'
LOG_FILE = 'badai_log.txt'

# === SECURITY HELPER ===
def sanitize_input(text):
    """Sanitize input untuk mencegah XSS"""
    if not text:
        return ""
    text = str(text)
    # Escape HTML
    text = escape(text)
    # Batasi panjang
    return text[:2000]

def is_valid_token(token):
    """Validasi format Telegram Bot Token"""
    if not token:
        return False
    pattern = r'^\d{8,10}:[A-Za-z0-9_-]{35}$'
    return re.match(pattern, token) is not None

def is_valid_chat_id(chat_id):
    """Validasi Chat ID"""
    if not chat_id:
        return False
    return chat_id.replace('-', '').replace(' ', '').isdigit()

def log_message(message, color="green"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except:
        pass
    logs.append({"time": timestamp, "message": message[:500], "color": color})
    if len(logs) > 300:
        logs.pop(0)
    print(log_entry)

def load_profile():
    default = {
        "token": "",
        "chat_id": "",
        "message": "",
        "count": 100,
        "rps": 30
    }
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**default, **data}
        except:
            pass
    return default

# ==================== HTML TEMPLATE (Hardened) ====================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>B.A.D.A.I 🌪️</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">
    <style>
        .log { font-family: 'Consolas', monospace; line-height: 1.5; }
        .input-field { transition: all 0.2s; }
        .input-field:focus { 
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3); 
            border-color: rgb(59 130 246);
        }
        @media (max-width: 640px) {
            .container { padding: 16px; }
            h1 { font-size: 2.25rem; }
            .btn-large { padding: 18px 24px; font-size: 1.1rem; }
        }
    </style>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen">
<div class="max-w-4xl mx-auto container p-4 sm:p-6">
    <!-- Pembungkus Utama -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 border-b border-gray-800 pb-6">
        
        <!-- Pembungkus Baru untuk Judul dan Sub-judul -->
        <div class="flex flex-col gap-1">
            <h1 class="text-4xl sm:text-5xl font-bold flex items-center gap-3">
                B.A.D.A.I <span class="text-5xl sm:text-6xl">🌪️</span>
            </h1>
            <!-- Ukuran teks h2 sedikit dikecilkan & diberi warna abu-abu agar kontrasnya cakep bro -->
            <h2 class="text-lg sm:text-xl font-medium text-gray-400">
                Bot Attack & Defense Asynchronous Interface
            </h2>
        </div>
        
        <!-- Pembungkus Tombol -->
        <div class="flex gap-3 w-full md:w-auto justify-start md:justify-end">
            <button onclick="showDisclaimer()" class="px-5 py-2.5 bg-orange-600 hover:bg-orange-700 rounded-2xl flex items-center gap-2 font-medium text-sm sm:text-base whitespace-nowrap">
                <i class="fas fa-exclamation-triangle"></i>🚧 Disclaimer
            </button>
            <button onclick="showAbout()" class="px-5 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-2xl flex items-center gap-2 font-medium text-sm sm:text-base whitespace-nowrap">
                <i class="fas fa-info-circle"></i>👷 About
            </button>
        </div>

    </div>
</div>

    <div class="space-y-6">
        <!-- Config -->
        <div class="bg-gray-900 rounded-3xl p-5 sm:p-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-5">
                <h2 class="text-xl font-semibold">🔧 API CONFIGURATION & PROFILE SCAMMER</h2>
                <div class="flex gap-3 w-full sm:w-auto">
                    <button onclick="loadProfile()" class="flex-1 sm:flex-none px-5 py-2.5 bg-purple-600 hover:bg-purple-700 rounded-2xl text-sm font-medium">
                        📂 Load Profile
                    </button>
                    <button onclick="saveProfile()" class="flex-1 sm:flex-none px-5 py-2.5 bg-blue-600 hover:bg-blue-700 rounded-2xl text-sm font-medium">
                        💾 Save Profile
                    </button>
                </div>
            </div>
            
            <div class="space-y-6">
                <div>
                    <label class="block text-sm text-gray-400 mb-1">🤖 Bot Token Telegram</label>
                    <input id="token" value="{{ profile.token }}" 
                           class="input-field w-full bg-gray-800 border border-gray-700 rounded-2xl px-5 py-4 text-base"
                           placeholder="Masukkan Bot Token Telegram">
                    <p class="text-xs text-gray-500 mt-1.5">PUT THE SCAMMER BOT TELEGRAM HERE</p>
                </div>

                <div>
                    <label class="block text-sm text-gray-400 mb-1">📢 Target Chat ID / Channel / Group ID</label>
                    <input id="chat_id" value="{{ profile.chat_id }}" 
                           class="input-field w-full bg-gray-800 border border-gray-700 rounded-2xl px-5 py-4 text-base"
                           placeholder="Contoh: -1001234567890 atau 8534803085">
                    <p class="text-xs text-gray-500 mt-1.5">MAKE SURE YOU HAVE CHANNEL ID FROM SCAMMER</p>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Number of Messages</label>
                        <input id="count" type="number" value="{{ profile.count }}" 
                               class="input-field w-full bg-gray-800 border border-gray-700 rounded-2xl px-5 py-4 text-base">
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Rate Per Second (RPS)</label>
                        <input id="rps" type="number" value="{{ profile.rps }}" 
                               class="input-field w-full bg-gray-800 border border-gray-700 rounded-2xl px-5 py-4 text-base">
                    </div>
                </div>
            </div>
        </div>

        <!-- Message -->
        <div class="bg-gray-900 rounded-3xl p-5 sm:p-6">
            <h2 class="text-xl font-semibold mb-3">📝 Payload Message (Supports HTML)</h2>
            <textarea id="message" rows="6" 
                      class="input-field w-full bg-gray-800 border border-gray-700 rounded-3xl p-5 text-base resize-y">{{ profile.message }}</textarea>
        </div>

        <!-- Action Buttons -->
        <div class="grid grid-cols-2 gap-4">
            <button onclick="startAttack()" id="startBtn" 
                    class="btn-large bg-emerald-600 hover:bg-emerald-700 py-6 text-xl font-bold rounded-3xl transition-all active:scale-95">
                🚀 START
            </button>
            <button onclick="stopAttack()" id="stopBtn" disabled
                    class="btn-large bg-red-600 hover:bg-red-700 py-6 text-xl font-bold rounded-3xl transition-all active:scale-95">
                🛑 STOP
            </button>
        </div>

        <!-- Progress -->
        <div class="bg-gray-900 rounded-3xl p-5 sm:p-6">
            <div class="flex justify-between text-sm mb-3">
                <span id="status" class="font-medium">Status: Siap</span>
                <span id="counter" class="font-mono">0 / 0</span>
            </div>
            <div class="h-4 bg-gray-800 rounded-2xl overflow-hidden">
                <div id="progress" class="h-full bg-emerald-500 w-0 transition-all duration-300"></div>
            </div>
        </div>

        <!-- Live Log -->
        <div class="bg-gray-900 rounded-3xl p-5 sm:p-6">
            <h3 class="font-semibold mb-3">📜 Live Log</h3>
            <pre id="log" class="log bg-black border border-gray-800 rounded-2xl p-4 sm:p-5 h-80 sm:h-96 overflow-auto text-sm"></pre>
        </div>
    </div>
</div>

<script>
let statusInterval;
let lastLogCount = 0;

function log(msg, color = 'text-green-400') {
    const logEl = document.getElementById('log');
    const time = new Date().toLocaleTimeString('id-ID', {hour12: false});
    logEl.innerHTML += `<span class="${color}">[${time}] ${msg}</span><br>`;
    logEl.scrollTop = logEl.scrollHeight;
}

async function saveProfile() {
    const data = {
        token: document.getElementById('token').value,
        chat_id: document.getElementById('chat_id').value,
        message: document.getElementById('message').value,
        count: document.getElementById('count').value,
        rps: document.getElementById('rps').value
    };
    const res = await fetch('/save_profile', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
    const result = await res.json();
    alert(result.message);
}

async function loadProfile() {
    const res = await fetch('/load_profile');
    const data = await res.json();
    if (data.success) {
        document.getElementById('token').value = data.token || '';
        document.getElementById('chat_id').value = data.chat_id || '';
        document.getElementById('message').value = data.message || '';
        document.getElementById('count').value = data.count || 100;
        document.getElementById('rps').value = data.rps || 50;
        alert("✅ Profil berhasil dimuat!");
    } else {
        alert("❌ " + (data.message || "Gagal memuat profil"));
    }
}

async function startAttack() {
    const data = {
        token: document.getElementById('token').value.trim(),
        chat_id: document.getElementById('chat_id').value.trim(),
        message: document.getElementById('message').value.trim(),
        count: parseInt(document.getElementById('count').value),
        rps: parseInt(document.getElementById('rps').value)
    };

    if (!data.token || !data.chat_id || !data.message) {
        alert("Token, Chat ID, dan Pesan wajib diisi!");
        return;
    }

    const res = await fetch('/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    const result = await res.json();
    log(result.message, result.success ? 'text-blue-400' : 'text-red-400');

    if (result.success) {
        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        statusInterval = setInterval(updateStatus, 600);
    }
}

async function stopAttack() {
    await fetch('/stop', { method: 'POST' });
    clearInterval(statusInterval);
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
}

async function updateStatus() {
    const res = await fetch('/status');
    const data = await res.json();
    
    document.getElementById('counter').textContent = `${data.success} / ${data.total}`;
    const progress = data.total > 0 ? (data.success + data.fail) / data.total * 100 : 0;
    document.getElementById('progress').style.width = `${Math.min(progress, 100)}%`;
    
    document.getElementById('status').innerHTML = data.is_running ? 
        `Attacking... <span class="text-emerald-400">(${data.success} ✅)</span> <span class="text-red-400">(${data.fail} ❌)</span>` : 'Finish';
    
    const logRes = await fetch('/logs');
    const logsData = await logRes.json();
    if (logsData.length > lastLogCount) {
        const newLogs = logsData.slice(lastLogCount);
        newLogs.forEach(l => log(l.message, l.color));
        lastLogCount = logsData.length;
    }
}

function showDisclaimer() {
    alert("⚠️ DISCLAIMER\\n\\nThis tool is created SOLELY for educational purposes, legal penetration testing, and Active Defense against cyber threats (such as scammers).\\nAny misuse is the sole responsibility of the user.");
}

function showAbout() {
    alert("B.A.D.A.I 🌪️\\nBot Attack & Defense Asynchronous Interface\\nCoded by xsanlahci © 2026 - thx to Aurel666");
}
</script>
</body>
</html>'''

# === ROUTES WITH SECURITY ===
@app.route('/')
def index():
    profile = load_profile()
    return render_template_string(HTML_TEMPLATE, profile=profile)

@app.route('/save_profile', methods=['POST'])
def save_profile():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"message": "Invalid data"}), 400

        # Sanitize
        safe_data = {
            "token": sanitize_input(data.get('token', '')),
            "chat_id": sanitize_input(data.get('chat_id', '')),
            "message": sanitize_input(data.get('message', '')),
            "count": int(data.get('count', 100)),
            "rps": int(data.get('rps', 30))
        }

        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(safe_data, f, indent=4)

        return jsonify({"message": "✅ Profil berhasil disimpan!"})
    except:
        return jsonify({"message": "❌ Gagal menyimpan profil"}), 400

@app.route('/load_profile')
def load_profile_route():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify({"success": True, **data})
        except:
            pass
    return jsonify({"success": False, "message": "Profil belum ada."})

@app.route('/start', methods=['POST'])
def start_attack():
    global is_running, success_count, fail_count, total_count, stop_flag, logs
    logs.clear()

    if is_running:
        return jsonify({"success": False, "message": "Serangan sudah berjalan"})

    try:
        data = request.get_json(force=True)
        token = sanitize_input(data.get('token', ''))
        chat_id = sanitize_input(data.get('chat_id', ''))
        message = sanitize_input(data.get('message', ''))
        count = min(int(data.get('count', 100)), 500)  # Limit maksimal
        rps = min(max(int(data.get('rps', 30)), 1), 50)  # Limit RPS

        if not is_valid_token(token):
            return jsonify({"success": False, "message": "Token Telegram tidak valid!"})

        if not is_valid_chat_id(chat_id):
            return jsonify({"success": False, "message": "Chat ID tidak valid!"})

        if not message:
            return jsonify({"success": False, "message": "Pesan tidak boleh kosong!"})

        is_running = True
        stop_flag = False
        success_count = 0
        fail_count = 0
        total_count = count

        threading.Thread(target=send_messages, args=(token, chat_id, message, count, rps), daemon=True).start()
        return jsonify({"success": True, "message": "The attack begins!"})
    except:
        return jsonify({"success": False, "message": "Input tidak valid!"}), 400

# Route lainnya tetap sama (stop, logs, status)

def send_messages(token, chat_id, message, count, rps):
    global success_count, fail_count, is_running, stop_flag
    import requests
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    sleep_time = 1.0 / rps

    log_message(f"🌪️ ATTACK STARTED | Total: {count} | RPS: {rps}", "blue")

    for i in range(1, count + 1):
        if stop_flag or not is_running:
            log_message("🛑 ATTACK STOP.", "yellow")
            break
        try:
            resp = requests.post(url, json={
                "chat_id": chat_id, 
                "text": message, 
                "parse_mode": "HTML"
            }, timeout=12)

            if resp.status_code == 200:
                success_count += 1
                log_message(f"[{i}/{count}] ✅ Sent", "green")
            elif resp.status_code in [401, 404]:
                fail_count += 1
                log_message(f"🎯 KILL-SWITCH! Target DOWN (HTTP {resp.status_code})", "red")
                is_running = False
                break
            else:
                fail_count += 1
                log_message(f"[{i}/{count}] ❌ Gagal (HTTP {resp.status_code})", "red")
        except Exception as e:
            fail_count += 1
            log_message(f"[{i}/{count}] ❌ Error: {str(e)[:80]}", "red")
        time.sleep(sleep_time)

    is_running = False
    log_message(f"🏁 FINISH | Success: {success_count} | Fail: {fail_count}", "blue")

@app.route('/stop', methods=['POST'])
def stop_attack():
    global stop_flag, is_running
    stop_flag = True
    is_running = False
    log_message("🛑 Serangan dihentikan manual", "yellow")
    return jsonify({"success": True})

@app.route('/logs')
def get_logs():
    return jsonify(logs[-300:])

@app.route('/status')
def get_status():
    return jsonify({
        "is_running": is_running,
        "success": success_count,
        "fail": fail_count,
        "total": total_count
    })

# Security Headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; style-src 'self' 'unsafe-inline';"
    return response

if __name__ == '__main__':
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()
    print("="*80)
    print("🌪️ B.A.D.A.I Flask - SECURED VERSION")
    print("🕷️ Web UI - 100% Mobile Responsive")
    print("🚇 Tunnel localhost to access your command center globally")
    print("👷 c0ded by XsanLahci 2026 - Thx to Aurel666")
    print("🌐 Running on http://127.0.0.1:7326")
    print("🔒 Security Hardening Applied")
    print("="*80)
    app.run(host='127.0.0.1', port=7326, debug=False)  # Hanya localhost
