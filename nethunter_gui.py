#!/usr/bin/env python3
"""
Project: Aero Nethunter
Version: v1.0 (Initial Release)
Description: Open-source network analysis and monitoring tool.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import scapy.all as scapy
from mac_vendor_lookup import MacLookup
import socket
import json
import csv
import psutil
import time
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Import new performance modules
try:
    from performance_manager import get_performance_manager, PerformanceManager
    from tray_manager import create_tray_manager, TrayNotificationManager
    from settings_dialog import SettingsDialog
    PERF_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"[Warning] Performance modules not available: {e}")
    PERF_MODULES_AVAILABLE = False

# Import new UI modules
try:
    from theme_manager import get_theme_manager, ThemeManager
    from ui_components import SearchFilterPanel, ToastNotification, StatCard, AnimatedButton
    from visualizations import TrafficGraph, DeviceTypePieChart, StatsDashboard
    from modern_components import GlassCard, GradientFrame, ModernButton, DeviceCard, Badge
    UI_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"[Warning] UI modules not available: {e}")
    UI_MODULES_AVAILABLE = False

# --- YAPILANDIRMA / İSİMLENDİRME ---
APP_VERSION = "v2.0"  # Performance Update
APP_NAME = "Aero Nethunter"  # <--- İSİM BURADA GÜNCELLENDİ

# --- DİL PAKETİ ---
LANG = {
    "en": {
        "title": f"{APP_NAME} {APP_VERSION}",
        "ctrl_panel": "⚙️ DASHBOARD",
        "target": "Target Network:",
        "auto": "🔍 Auto-Detect",
        "ports": "Target Ports:",
        "chk_port": "Enable Service Scan",
        "btn_scan": "▶ START SCAN",
        "btn_stop": "⏹ STOP SCAN",
        "btn_monitor": "📊 TRAFFIC MONITOR",
        "btn_stop_mon": "⏸ PAUSE MONITOR",
        "btn_web": "🌐 WEB UI",
        "btn_export": "💾 EXPORT CSV",
        "lbl_stats": "Devices Found: {} | Active Traffic: {}",
        "col_ip": "IP Address",
        "col_mac": "MAC Address",
        "col_vendor": "Vendor",
        "col_host": "Hostname",
        "col_type": "Device Type",
        "col_ports": "Open Services",
        "col_rx": "↓ Download",
        "col_tx": "↑ Upload",
        "status_ready": "Ready to scan.",
        "status_scan": "Scanning network...",
        "ctx_known": "Mark as Known",
        "ctx_unauth": "Mark as Unknown",
        "ctx_wol": "Send Wake-on-LAN"
    },
    "tr": {
        "title": f"{APP_NAME} {APP_VERSION}",
        "ctrl_panel": "⚙️ KONTROL PANELİ",
        "target": "Hedef Ağ:",
        "auto": "🔍 Otomatik Bul",
        "ports": "Hedef Portlar:",
        "chk_port": "Servis Taraması",
        "btn_scan": "▶ TARAMAYI BAŞLAT",
        "btn_stop": "⏹ DURDUR",
        "btn_monitor": "📊 TRAFİK İZLE",
        "btn_stop_mon": "⏸ DURAKLAT",
        "btn_web": "🌐 WEB ARAYÜZÜ",
        "btn_export": "💾 DIŞA AKTAR",
        "lbl_stats": "Bulunan: {} | Aktif Trafik: {}",
        "col_ip": "IP Adresi",
        "col_mac": "MAC Adresi",
        "col_vendor": "Üretici",
        "col_host": "Cihaz Adı",
        "col_type": "Cihaz Tipi",
        "col_ports": "Açık Servisler",
        "col_rx": "↓ İndirme",
        "col_tx": "↑ Yükleme",
        "status_ready": "Taramaya hazır.",
        "status_scan": "Ağ taranıyor...",
        "ctx_known": "Tanıdık İşaretle",
        "ctx_unauth": "Yabancı İşaretle",
        "ctx_wol": "Wake-on-LAN Gönder",
        "btn_settings": "⚙️ AYARLAR",
        "lbl_perf": "CPU: {}% | RAM: {} MB | Devices: {} | Cache: {}%"
    }
}

class AeroNethunterGUI:  # <--- SINIF İSMİ GÜNCELLENDİ
    def __init__(self, root):
        self.root = root
        self.lang_code = "tr"
        self.t = LANG[self.lang_code]
        
        # Load configuration
        self.config = self.load_config()
        
        # Pencere Başlığı Ayarı
        self.root.title(self.t["title"])
        self.root.geometry("1300x800")
        
        # Değişkenler
        self.scanning = False
        self.monitoring = False
        self.known_macs = set()
        self.current_devices = {} 
        self.traffic_stats = {}
        self.mac_lookup = MacLookup()
        
        # Performance Manager
        if PERF_MODULES_AVAILABLE:
            self.perf_manager = PerformanceManager(self.config)
            self.thread_pool = ThreadPoolExecutor(max_workers=self.config.get("thread_pool_size", 10))
        else:
            self.perf_manager = None
            self.thread_pool = None
        
        # System Tray
        self.tray_manager = None
        self.tray_notifications = None
        
        # UI update throttling
        self.last_ui_update = 0
        self.ui_update_scheduled = False
        
        # Theme Manager
        if UI_MODULES_AVAILABLE:
            self.theme_manager = get_theme_manager()
            self.theme = self.theme_manager.current_theme
            self.colors = self.theme.colors
            self.theme_manager.register_callback(self.on_theme_changed)
        else:
            self.theme_manager = None
            self.theme = None
            # Renk Teması (Dark Mode)
            self.colors = {
                "bg_main": "#1e1e2e", 
                "bg_side": "#11111b", 
                "accent": "#89b4fa",
                "text": "#cdd6f4",
                "success": "#a6e3a1", 
                "warn": "#f9e2af", 
                "err": "#f38ba8",
                "bg_card": "#313244",
                "hover": "#45475a"
            }
        
        # Toast notification system
        if UI_MODULES_AVAILABLE:
            self.toast = None  # Will be initialized after root is ready
        
        # Traffic visualization
        self.traffic_graph = None
        self.device_pie_chart = None
        
        # Search/Filter
        self.search_filter_panel = None
        self.filtered_devices = None
        
        self.load_data()
        self.setup_ui()
        self.auto_detect_network()
        
        # Initialize toast after root is ready
        if UI_MODULES_AVAILABLE:
            self.root.after(100, self.init_toast)
        
        # Setup tray after UI
        if PERF_MODULES_AVAILABLE and self.config.get("tray_enabled", True):
            self.setup_tray()
        
        # Resource monitor update loop
        if self.config.get("show_resources", True):
            self.update_resource_monitor()
        
        # Traffic graph update loop
        if UI_MODULES_AVAILABLE:
            self.update_traffic_graph()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def switch_language(self):
        self.lang_code = "en" if self.lang_code == "tr" else "tr"
        self.t = LANG[self.lang_code]
        self.refresh_ui_text()

    def setup_ui(self):
        # Stil Ayarları
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                        background=self.colors["bg_main"], 
                        foreground="white", 
                        fieldbackground=self.colors["bg_main"],
                        rowheight=30, borderwidth=0, font=("Consolas", 10)) 
        style.configure("Treeview.Heading", 
                        background=self.colors["bg_side"], 
                        foreground=self.colors["accent"], 
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", self.colors["accent"])])

        main_frame = tk.Frame(self.root, bg=self.colors["bg_main"])
        main_frame.pack(fill="both", expand=True)

        # --- YAN MENÜ (SIDEBAR) with Gradient ---
        if UI_MODULES_AVAILABLE:
            # Use gradient sidebar
            side = GradientFrame(
                main_frame,
                color1=self.colors["bg_side"],
                color2=self.colors.get("bg_main", "#0a0e27"),
                direction="vertical",
                width=320
            )
            side.pack(side="left", fill="y")
        else:
            # Fallback to regular frame
            side = tk.Frame(main_frame, bg=self.colors["bg_side"], width=320)
            side.pack(side="left", fill="y")
        
        side.pack_propagate(False)

        # --- LOGO / BAŞLIK BÖLÜMÜ ---
        header_container = tk.Frame(side, bg=self.colors["bg_side"])
        header_container.pack(pady=(30, 5))
        
        tk.Label(header_container, text=APP_NAME, font=("Segoe UI", 26, "bold"), 
                bg=self.colors["bg_side"], fg=self.colors["accent"]).pack(pady=(0, 5))
        
        # Versiyon Badge
        if UI_MODULES_AVAILABLE:
            Badge(header_container, f"v{APP_VERSION[1:]}", "info", self.colors).pack()
        else:
            tk.Label(header_container, text=f"Version {APP_VERSION}", font=("Consolas", 10), 
                    bg=self.colors["bg_side"], fg=self.colors["text_dim"]).pack()
        
        # Visual separator
        tk.Frame(side, bg=self.colors["accent"], height=2).pack(fill="x", padx=30, pady=20)

        # Dil Değiştirme Butonu
        self.btn_lang = tk.Button(side, text="TR / EN", command=self.switch_language, bg="#313244", fg="white", relief="flat", width=10)
        self.btn_lang.pack(pady=5)

        tk.Label(side, text="Target / Hedef", font=("Segoe UI", 10, "bold"), bg=self.colors["bg_side"], fg="gray").pack(pady=(20, 5), anchor="w", padx=20)

        # Giriş Alanları
        self.entry_target = tk.Entry(side, bg="#313244", fg="white", relief="flat", font=("Consolas", 11))
        self.entry_target.pack(fill="x", padx=20, pady=5)

        self.btn_auto = tk.Button(side, text=self.t["auto"], command=self.auto_detect_network, bg="#45475a", fg="white", relief="flat")
        self.btn_auto.pack(fill="x", padx=20, pady=2)
        
        # Theme Selector (if available)
        if UI_MODULES_AVAILABLE and self.theme_manager:
            theme_frame = tk.Frame(side, bg=self.colors["bg_side"])
            theme_frame.pack(fill="x", padx=20, pady=(15, 5))
            
            tk.Label(theme_frame, text="🎨 Theme:", font=("Segoe UI", 9, "bold"), bg=self.colors["bg_side"], fg=self.colors["text_dim"]).pack(side="left", padx=(0, 5))
            
            self.theme_var = tk.StringVar(value=self.theme.name)
            theme_combo = ttk.Combobox(
                theme_frame,
                textvariable=self.theme_var,
                values=self.theme_manager.get_available_themes(),
                state="readonly",
                width=12,
                font=("Consolas", 9)
            )
            theme_combo.pack(side="left")
            theme_combo.bind("<<ComboboxSelected>>", lambda e: self.change_theme(self.theme_var.get()))

        self.entry_ports = tk.Entry(side, bg="#313244", fg="white", relief="flat", font=("Consolas", 11))
        self.entry_ports.insert(0, "22,80,443,3389")
        self.entry_ports.pack(fill="x", padx=20, pady=(15, 5))

        self.chk_var = tk.BooleanVar(value=True)
        self.chk_port = tk.Checkbutton(side, text=self.t["chk_port"], variable=self.chk_var, bg=self.colors["bg_side"], fg="white", selectcolor=self.colors["bg_side"], activebackground=self.colors["bg_side"])
        self.chk_port.pack(fill="x", padx=15, pady=5)

        # Aksiyon Butonları
        tk.Label(side, text="Actions / İşlemler", font=("Segoe UI", 10, "bold"), bg=self.colors["bg_side"], fg="gray").pack(pady=(20, 10), anchor="w", padx=20)

        # Use modern buttons if available
        if UI_MODULES_AVAILABLE:
            # Modern scan button
            self.btn_scan = ModernButton(
                side, 
                text=self.t["btn_scan"],
                command=self.toggle_scan,
                colors=self.colors,
                width=280, 
                height=50
            )
            self.btn_scan.pack(padx=20, pady=8)
            
            # Modern monitor button  
            self.btn_monitor = ModernButton(
                side,
                text=self.t["btn_monitor"],
                command=self.toggle_monitoring,
                colors={**self.colors, "accent": self.colors.get("accent_alt", "#ff2e97")},
                width=280,
                height=45
            )
            self.btn_monitor.pack(padx=20, pady=8)
        else:
            # Fallback to standard buttons
            self.btn_scan = tk.Button(side, text=self.t["btn_scan"], command=self.toggle_scan, 
                                     bg=self.colors["success"], fg="#1e1e2e", font=("Segoe UI", 11, "bold"), 
                                     height=2, relief="flat", cursor="hand2")
            self.btn_scan.pack(fill="x", padx=20, pady=5)

            self.btn_monitor = tk.Button(side, text=self.t["btn_monitor"], command=self.toggle_monitoring, 
                                        bg=self.colors["accent"], fg="#1e1e2e", font=("Segoe UI", 10, "bold"), 
                                        relief="flat", cursor="hand2")
            self.btn_monitor.pack(fill="x", padx=20, pady=5)

        # Alt Butonlar
        btn_frame = tk.Frame(side, bg=self.colors["bg_side"])
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        self.btn_web = tk.Button(btn_frame, text="WEB UI", command=self.launch_web_server, bg="#f38ba8", fg="#1e1e2e", font=("Segoe UI", 9, "bold"), relief="flat", width=12)
        self.btn_web.pack(side="left", padx=(0, 5))
        
        self.btn_export = tk.Button(btn_frame, text="CSV", command=self.export_data, bg=self.colors["warn"], fg="#1e1e2e", font=("Segoe UI", 9, "bold"), relief="flat", width=12)
        self.btn_export.pack(side="right")
        
        # Settings Button
        if PERF_MODULES_AVAILABLE:
            self.btn_settings = tk.Button(side, text="⚙️ Settings", command=self.open_settings, bg="#45475a", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2")
            self.btn_settings.pack(fill="x", padx=20, pady=10)
        
        # Performance Monitor Label
        self.lbl_perf = tk.Label(side, text="", font=("Consolas", 8), bg=self.colors["bg_side"], fg=self.colors["accent"], wraplength=260, justify="left")
        self.lbl_perf.pack(side="bottom", pady=(10, 5))

        self.lbl_stats = tk.Label(side, text="Idle", font=("Consolas", 9), bg=self.colors["bg_side"], fg="gray")
        self.lbl_stats.pack(side="bottom", pady=(5, 20))

        # --- ANA İÇERİK (TABLO) ---
        content = tk.Frame(main_frame, bg=self.colors["bg_main"])
        content.pack(side="right", fill="both", expand=True)

        cols = ("col_ip", "col_mac", "col_vendor", "col_host", "col_type", "col_ports", "col_rx", "col_tx")
        self.tree = ttk.Treeview(content, columns=cols, show="headings")
        
        widths = [130, 150, 160, 130, 110, 180, 100, 100]
        for i, col in enumerate(cols):
            self.tree.heading(col, text=self.t[col])
            self.tree.column(col, width=widths[i], anchor="center")

        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

        # Renkli Etiketler
        self.tree.tag_configure('new', background=self.colors["err"], foreground="#1e1e2e")
        self.tree.tag_configure('known', background=self.colors["bg_main"], foreground="white")
        self.tree.tag_configure('me', background=self.colors["accent"], foreground="#1e1e2e")

        # Sağ Tık Menüsü
        self.ctx_menu = tk.Menu(self.root, tearoff=0)
        self.ctx_menu.add_command(label=self.t["ctx_known"], command=lambda: self.mark_device(True))
        self.ctx_menu.add_command(label=self.t["ctx_unauth"], command=lambda: self.mark_device(False))
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label=self.t["ctx_wol"], command=self.send_wol)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def refresh_ui_text(self):
        # Pencere başlığını güncelle
        self.root.title(self.t["title"])
        self.btn_auto.config(text=self.t["auto"])
        self.chk_port.config(text=self.t["chk_port"])
        self.btn_scan.config(text=self.t["btn_stop"] if self.scanning else self.t["btn_scan"])
        self.btn_monitor.config(text=self.t["btn_stop_mon"] if self.monitoring else self.t["btn_monitor"])
        self.btn_web.config(text="WEB UI") 
        self.btn_export.config(text="CSV") 
        
        cols = ("col_ip", "col_mac", "col_vendor", "col_host", "col_type", "col_ports", "col_rx", "col_tx")
        for col in cols:
            self.tree.heading(col, text=self.t[col])
            
        self.ctx_menu.entryconfigure(0, label=self.t["ctx_known"])
        self.ctx_menu.entryconfigure(1, label=self.t["ctx_unauth"])
        self.ctx_menu.entryconfigure(3, label=self.t["ctx_wol"])

    def auto_detect_network(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.local_ip = s.getsockname()[0]
            s.close()
            parts = self.local_ip.split('.')
            network = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            self.entry_target.delete(0, tk.END)
            self.entry_target.insert(0, network)
        except: pass

    def toggle_scan(self):
        if self.scanning:
            self.scanning = False
            if UI_MODULES_AVAILABLE and isinstance(self.btn_scan, ModernButton):
                self.btn_scan.text = self.t["btn_scan"]
                self.btn_scan.bg_color = self.colors["success"]
                self.btn_scan._draw()
            else:
                self.btn_scan.config(text=self.t["btn_scan"], bg=self.colors["success"])
        else:
            self.scanning = True
            if UI_MODULES_AVAILABLE and isinstance(self.btn_scan, ModernButton):
                self.btn_scan.text = self.t["btn_stop"]
                self.btn_scan.bg_color = self.colors["err"]
                self.btn_scan._draw()
            else:
                self.btn_scan.config(text=self.t["btn_stop"], bg=self.colors["err"])
            threading.Thread(target=self.scan_loop, daemon=True).start()

    def scan_loop(self):
        target = self.entry_target.get()
        scan_interval = self.config.get("scan_interval", 3)
        arp_timeout = self.config.get("arp_timeout", 2)
        
        while self.scanning:
            try:
                # Start performance timer
                if self.perf_manager:
                    start_time = self.perf_manager.start_scan_timer()
                
                arp_req = scapy.ARP(pdst=target)
                broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
                answered = scapy.srp(broadcast/arp_req, timeout=arp_timeout, verbose=False)[0]
                
                for elem in answered:
                    ip = elem[1].psrc
                    mac = elem[1].hwsrc
                    
                    if mac not in self.current_devices:
                        self.register_device(ip, mac)
                    else:
                        self.current_devices[mac]["ip"] = ip
                
                # End performance timer
                if self.perf_manager:
                    self.perf_manager.end_scan_timer(start_time)
                    self.perf_manager.resource_monitor.update_device_count(len(self.current_devices))
                
                self.save_live_data()
                self.schedule_ui_update()
                time.sleep(scan_interval)
            except Exception as e:
                print(e)
                self.scanning = False

    def register_device(self, ip, mac):
        # Use cached MAC vendor lookup
        if self.perf_manager:
            vendor = self.perf_manager.mac_cache.lookup(mac, self.mac_lookup.lookup)
        else:
            try: vendor = self.mac_lookup.lookup(mac)
            except: vendor = "Unknown"
        
        try: hostname = socket.gethostbyaddr(ip)[0]
        except: hostname = "?"
        
        v_low = vendor.lower()
        if "apple" in v_low or "samsung" in v_low: dtype = "📱 Mobile"
        elif "intel" in v_low or "msi" in v_low: dtype = "💻 PC"
        elif "router" in v_low or "gateway" in v_low: dtype = "🌐 Net"
        else: dtype = "❓ Unknown"

        is_known = mac in self.known_macs

        self.current_devices[mac] = {
            "ip": ip, "mac": mac, "vendor": vendor, "host": hostname,
            "type": dtype, "ports": "", "is_known": is_known
        }
        
        # Notify if new unknown device
        if not is_known and self.tray_notifications:
            self.tray_notifications.notify_new_device(self.current_devices[mac])
        
        if self.chk_var.get():
            if self.thread_pool:
                # Use thread pool for port scanning
                self.thread_pool.submit(self.scan_services, ip, mac)
            else:
                threading.Thread(target=self.scan_services, args=(ip, mac), daemon=True).start()

    def scan_services(self, ip, mac):
        ports_str = self.entry_ports.get()
        target_ports = [int(p) for p in ports_str.split(',') if p.isdigit()]
        found_services = []
        timeout = self.config.get("port_scan_timeout", 1.0)
        
        for p in target_ports:
            # Check connection pool availability
            if self.perf_manager and self.perf_manager.connection_pool:
                if not self.perf_manager.connection_pool.acquire():
                    time.sleep(0.1)  # Wait briefly if pool exhausted
                    continue
            
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(timeout)
                result = s.connect_ex((ip, p))
                if result == 0:
                    try: banner = s.recv(1024).decode().strip()
                    except: banner = ""
                    
                    try: svc_name = socket.getservbyport(p)
                    except: svc_name = "unknown"
                    
                    info = f"{p} ({svc_name})"
                    if banner:
                        clean_banner = banner[:15].replace("SSH-2.0-", "")
                        info += f" [{clean_banner}]"
                    found_services.append(info)
                s.close()
            except: pass
            finally:
                if self.perf_manager and self.perf_manager.connection_pool:
                    self.perf_manager.connection_pool.release()
        
        if mac in self.current_devices:
            self.current_devices[mac]["ports"] = ", ".join(found_services) if found_services else ""
            self.schedule_ui_update()

    def toggle_monitoring(self):
        if self.monitoring:
            self.monitoring = False
            self.btn_monitor.config(text=self.t["btn_monitor"], bg=self.colors["accent"])
        else:
            self.monitoring = True
            self.btn_monitor.config(text=self.t["btn_stop_mon"], bg=self.colors["warn"])
            threading.Thread(target=self.monitor_loop, daemon=True).start()

    def monitor_loop(self):
        while self.monitoring:
            def packet_handler(pkt):
                if not self.monitoring: return
                try:
                    if pkt.haslayer(scapy.Ether):
                        src = pkt[scapy.Ether].src
                        dst = pkt[scapy.Ether].dst
                        length = len(pkt)
                        if src in self.traffic_stats: self.traffic_stats[src]["tx"] += length
                        else: self.traffic_stats[src] = {"rx": 0, "tx": length}
                        if dst in self.traffic_stats: self.traffic_stats[dst]["rx"] += length
                        else: self.traffic_stats[dst] = {"rx": length, "tx": 0}
                except: pass
            scapy.sniff(prn=packet_handler, timeout=2, store=0)
            self.root.after(0, self.refresh_tree)

    def refresh_tree(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        total_rx = 0
        total_tx = 0
        
        for mac, d in self.current_devices.items():
            stats = self.traffic_stats.get(mac, {"rx": 0, "tx": 0})
            rx_fmt = f"{stats['rx']/1024:.1f} KB"
            tx_fmt = f"{stats['tx']/1024:.1f} KB"
            total_rx += stats['rx']
            total_tx += stats['tx']

            if mac == self.get_my_mac(): tag = "me"
            elif d["is_known"]: tag = "known"
            else: tag = "new"

            self.tree.insert("", "end", values=(
                d["ip"], d["mac"], d["vendor"], d["host"], 
                d["type"], d["ports"], rx_fmt, tx_fmt
            ), tags=(tag,))
            
        self.lbl_stats.config(text=self.t["lbl_stats"].format(len(self.current_devices), f"↓{total_rx/1024:.1f}KB ↑{total_tx/1024:.1f}KB"))

    def launch_web_server(self):
        try:
            if os.name == 'nt': subprocess.Popen(["python", "web_server.py"], shell=True)
            else: subprocess.Popen(["python3", "web_server.py"])
            messagebox.showinfo("Web Server", "Server started at: http://localhost:5000")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_live_data(self):
        data = {"devices": list(self.current_devices.values())}
        try:
            with open("live_data.json", "w") as f: json.dump(data, f)
        except: pass

    def get_my_mac(self):
        try: return scapy.get_if_hwaddr(scapy.conf.iface)
        except: return ""

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.ctx_menu.post(event.x_root, event.y_root)

    def mark_device(self, is_known):
        sel = self.tree.selection()
        if sel:
            mac = self.tree.item(sel[0])['values'][1]
            if mac in self.current_devices:
                self.current_devices[mac]["is_known"] = is_known
                if is_known: self.known_macs.add(mac)
                else: self.known_macs.discard(mac)
                self.save_data()
                self.refresh_tree()

    def send_wol(self):
        sel = self.tree.selection()
        if sel:
            mac = self.tree.item(sel[0])['values'][1]
            packet = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")/scapy.IP(dst="255.255.255.255")/scapy.UDP(dport=9)/scapy.Raw(load=bytes.fromhex('FF'*6 + mac.replace(':','')*16))
            scapy.sendp(packet, verbose=0)
            messagebox.showinfo("WOL", f"Magic Packet sent to {mac}")

    def load_data(self):
        if os.path.exists("known.json"):
            with open("known.json") as f: self.known_macs = set(json.load(f))

    def save_data(self):
        with open("known.json", "w") as f: json.dump(list(self.known_macs), f)

    def export_data(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv")
        if f:
            with open(f, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["IP", "MAC", "Vendor", "Hostname", "Type", "Ports"])
                for mac, d in self.current_devices.items():
                    writer.writerow([d["ip"], d["mac"], d["vendor"], d["host"], d["type"], d["ports"]])
            messagebox.showinfo("Export", "Saved successfully!")
    
    # --- NEW PERFORMANCE METHODS ---
    
    def load_config(self):
        """Load configuration from file"""
        try:
            from settings_dialog import SettingsDialog
            return SettingsDialog.load_config()
        except:
            return {
                "scan_interval": 3,
                "thread_pool_size": 10,
                "cache_size": 1000,
                "max_connections": 50,
                "tray_enabled": True,
                "minimize_to_tray": True,
                "notifications_enabled": True,
                "show_resources": True,
                "port_scan_timeout": 1.0,
                "arp_timeout": 2,
                "ui_update_interval": 500
            }
    
    def setup_tray(self):
        """Setup system tray icon"""
        try:
            self.tray_manager = create_tray_manager(self)
            self.tray_notifications = TrayNotificationManager(self.tray_manager)
            self.tray_manager.start()
            print("[Tray] System tray initialized")
        except Exception as e:
            print(f"[Tray] Failed to initialize: {e}")
    
    def open_settings(self):
        """Open settings dialog"""
        try:
            dialog = SettingsDialog(self.root, self.config, on_save=self.on_settings_saved)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings: {e}")
    
    def on_settings_saved(self, new_config):
        """Handle settings save"""
        self.config = new_config
        # Update performance manager
        if self.perf_manager:
            self.perf_manager.config = new_config
            # Recreate thread pool if size changed
            if self.thread_pool:
                self.thread_pool.shutdown(wait=False)
                self.thread_pool = ThreadPoolExecutor(max_workers=new_config.get("thread_pool_size", 10))
    
    def schedule_ui_update(self):
        """Schedule UI update with throttling"""
        if self.ui_update_scheduled:
            return
        
        interval = self.config.get("ui_update_interval", 500)
        self.ui_update_scheduled = True
        self.root.after(interval, self._do_ui_update)
    
    def _do_ui_update(self):
        """Actually perform UI update"""
        self.refresh_tree()
        self.ui_update_scheduled = False
    
    def update_resource_monitor(self):
        """Update resource monitor display"""
        if not self.perf_manager:
            return
        
        try:
            stats = self.perf_manager.resource_monitor.get_stats()
            cache_stats = self.perf_manager.mac_cache.get_stats()
            
            # Update performance label
            perf_text = self.t.get("lbl_perf", "CPU: {}% | RAM: {} MB | Devices: {} | Cache: {}%").format(
                stats["cpu_percent"],
                stats["memory_mb"],
                stats["device_count"],
                round(cache_stats["hit_rate"])
            )
            
            if hasattr(self, 'lbl_perf'):
                self.lbl_perf.config(text=perf_text)
            
            # Update tray tooltip
            if self.tray_manager:
                tooltip = f"{APP_NAME} - {stats['device_count']} devices"
                self.tray_manager.update_tooltip(tooltip)
        
        except Exception as e:
            print(f"[Monitor] Error: {e}")
        
        # Schedule next update
        self.root.after(2000, self.update_resource_monitor)
    
    def on_closing(self):
        """Handle window close event"""
        if self.config.get("minimize_to_tray", True) and self.tray_manager:
            # Minimize to tray instead of closing
            self.root.withdraw()
            if self.tray_manager:
                self.tray_manager.set_visible_state(False)
                self.tray_manager.notify("Aero Nethunter", "Running in background. Right-click tray icon to show.")
        else:
            # Actually quit
            self.cleanup_and_exit()
    
    def cleanup_and_exit(self):
        """Cleanup and exit application"""
        # Stop scanning
        self.scanning = False
        self.monitoring = False
        
        # Cleanup performance manager
        if self.perf_manager:
            self.perf_manager.cleanup()
        
        # Shutdown thread pool
        if self.thread_pool:
            self.thread_pool.shutdown(wait=False)
        
        # Stop tray
        if self.tray_manager:
            self.tray_manager.stop()
        
        # Quit
        self.root.quit()
    
    # --- NEW UI METHODS ---
    
    def init_toast(self):
        """Initialize toast notification system"""
        if UI_MODULES_AVAILABLE:
            self.toast = ToastNotification(self.root, colors=self.colors)
    
    def change_theme(self, theme_name):
        """Change application theme"""
        if self.theme_manager and self.theme_manager.set_theme(theme_name):
            # Theme changed callback will be triggered
            pass
    
    def on_theme_changed(self, new_theme):
        """Handle theme change"""
        self.theme = new_theme
        self.colors = new_theme.colors
        
        # Show toast notification
        if self.toast:
            self.toast.show(f"Theme changed to {new_theme.name}", "success", 2000)
        
        # Note: Full UI refresh would require recreating widgets
        # For simplicity, new theme applies on restart
        messagebox.showinfo("Theme Changed",
                           f"Theme set to '{new_theme.name}'. Restart the application to see full changes.")
    
    def update_traffic_graph(self):
        """Update traffic graph periodically"""
        if not self.traffic_graph or not UI_MODULES_AVAILABLE:
            self.root.after(2000, self.update_traffic_graph)
            return
        
        try:
            # Calculate total traffic
            total_download = 0
            total_upload = 0
            
            for mac, stats in self.traffic_stats.items():
                total_download += stats.get("rx", 0)
                total_upload += stats.get("tx", 0)
            
            # Convert to KB/s (approximate)
            download_kbps = (total_download / 1024) / 2  # Divided by 2 sec interval
            upload_kbps = (total_upload / 1024) / 2
            
            self.traffic_graph.update(download_kbps, upload_kbps)
        except Exception as e:
            print(f"[Graph] Update error: {e}")
        
        # Schedule next update
        self.root.after(2000, self.update_traffic_graph)
    
    def apply_search_filter(self, query="", filters=None):
        """Apply search and filter to device list"""
        if filters is None:
            filters = {}
        
        self.filtered_devices = {}
        query_lower = query.lower()
        
        for mac, device in self.current_devices.items():
            # Search filter
            if query:
                searchable = f"{device['ip']} {device['mac']} {device['vendor']} {device['host']}".lower()
                if query_lower not in searchable:
                    continue
            
            # Type filters
            if filters.get("mobile") and "Mobile" not in device.get("type", ""):
                continue
            if filters.get("pc") and "PC" not in device.get("type", ""):
                continue
            if filters.get("router") and "Net" not in device.get("type", ""):
                continue
            if filters.get("new") and device.get("is_known", False):
                continue
            
            self.filtered_devices[mac] = device
        
        self.refresh_tree()
    
    def get_device_type_stats(self):
        """Get device type distribution for pie chart"""
        stats = {}
        for device in self.current_devices.values():
            device_type = device.get("type", "❓ Unknown")
            stats[device_type] = stats.get(device_type, 0) + 1
        return stats

if __name__ == "__main__":
    root = tk.Tk()
    app = AeroNethunterGUI(root)
    root.mainloop()