#!/usr/bin/env python3
"""
Settings Dialog for Aero Nethunter
Configurable performance and system settings
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class SettingsDialog:
    """Settings configuration dialog"""
    
    def __init__(self, parent, config, on_save=None):
        """
        Initialize settings dialog
        Args:
            parent: Parent window
            config: Current configuration dict
            on_save: Callback when settings are saved
        """
        self.parent = parent
        self.config = config.copy()
        self.on_save = on_save
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ Settings - Aero Nethunter")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        
        # Colors
        self.colors = {
            "bg": "#1e1e2e",
            "fg": "#cdd6f4",
            "accent": "#89b4fa",
            "bg_dark": "#11111b"
        }
        
        self.dialog.configure(bg=self.colors["bg"])
        
        self.setup_ui()
        
        # Center window
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def setup_ui(self):
        """Setup UI components"""
        # Title
        title = tk.Label(
            self.dialog, 
            text="⚙️ Settings", 
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        title.pack(pady=20)
        
        # Notebook (tabs)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=self.colors["bg_dark"], 
                       foreground=self.colors["fg"], padding=[20, 10])
        style.map("TNotebook.Tab", background=[("selected", self.colors["accent"])],
                 foreground=[("selected", "#1e1e2e")])
        
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Performance Tab
        perf_frame = tk.Frame(notebook, bg=self.colors["bg"])
        notebook.add(perf_frame, text="⚡ Performance")
        self.setup_performance_tab(perf_frame)
        
        # System Tab
        system_frame = tk.Frame(notebook, bg=self.colors["bg"])
        notebook.add(system_frame, text="🖥️ System")
        self.setup_system_tab(system_frame)
        
        # Advanced Tab
        advanced_frame = tk.Frame(notebook, bg=self.colors["bg"])
        notebook.add(advanced_frame, text="🔧 Advanced")
        self.setup_advanced_tab(advanced_frame)
        
        # Buttons
        btn_frame = tk.Frame(self.dialog, bg=self.colors["bg"])
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Button(
            btn_frame,
            text="💾 Save",
            command=self.save_settings,
            bg="#a6e3a1",
            fg="#1e1e2e",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            width=15
        ).pack(side="right", padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Cancel",
            command=self.dialog.destroy,
            bg="#f38ba8",
            fg="#1e1e2e",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            width=15
        ).pack(side="right")
    
    def create_labeled_entry(self, parent, label_text, var, row):
        """Create a labeled entry field"""
        tk.Label(
            parent,
            text=label_text,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Segoe UI", 10)
        ).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        
        entry = tk.Entry(
            parent,
            textvariable=var,
            bg="#313244",
            fg="white",
            relief="flat",
            font=("Consolas", 10),
            width=20
        )
        entry.grid(row=row, column=1, sticky="ew", padx=10, pady=8)
        
        return entry
    
    def create_labeled_scale(self, parent, label_text, var, from_, to_, row):
        """Create a labeled scale"""
        tk.Label(
            parent,
            text=label_text,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Segoe UI", 10)
        ).grid(row=row, column=0, sticky="w", padx=10, pady=8)
        
        scale_frame = tk.Frame(parent, bg=self.colors["bg"])
        scale_frame.grid(row=row, column=1, sticky="ew", padx=10, pady=8)
        
        scale = tk.Scale(
            scale_frame,
            from_=from_,
            to=to_,
            orient="horizontal",
            variable=var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            highlightthickness=0,
            troughcolor="#313244",
            activebackground=self.colors["accent"]
        )
        scale.pack(side="left", fill="x", expand=True)
        
        value_label = tk.Label(
            scale_frame,
            textvariable=var,
            bg=self.colors["bg"],
            fg=self.colors["accent"],
            font=("Consolas", 10, "bold"),
            width=5
        )
        value_label.pack(side="right", padx=5)
        
        return scale
    
    def setup_performance_tab(self, parent):
        """Setup performance settings tab"""
        container = tk.Frame(parent, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.grid_columnconfigure(1, weight=1)
        
        # Scan Interval
        self.scan_interval_var = tk.IntVar(value=self.config.get("scan_interval", 3))
        self.create_labeled_scale(
            container,
            "Scan Interval (seconds):",
            self.scan_interval_var,
            1, 30, 0
        )
        
        # Thread Pool Size
        self.thread_pool_var = tk.IntVar(value=self.config.get("thread_pool_size", 10))
        self.create_labeled_scale(
            container,
            "Thread Pool Size:",
            self.thread_pool_var,
            5, 50, 1
        )
        
        # Cache Size
        self.cache_size_var = tk.IntVar(value=self.config.get("cache_size", 1000))
        self.create_labeled_scale(
            container,
            "MAC Cache Size:",
            self.cache_size_var,
            100, 5000, 2
        )
        
        # Max Connections
        self.max_conn_var = tk.IntVar(value=self.config.get("max_connections", 50))
        self.create_labeled_scale(
            container,
            "Max Connections:",
            self.max_conn_var,
            10, 200, 3
        )
        
        # Info label
        info = tk.Label(
            container,
            text="💡 Higher values = better performance but more resource usage",
            bg=self.colors["bg"],
            fg="gray",
            font=("Segoe UI", 9),
            wraplength=500,
            justify="left"
        )
        info.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=20)
    
    def setup_system_tab(self, parent):
        """Setup system settings tab"""
        container = tk.Frame(parent, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Enable Tray
        self.tray_enabled_var = tk.BooleanVar(value=self.config.get("tray_enabled", True))
        tk.Checkbutton(
            container,
            text="📌 Enable System Tray Icon",
            variable=self.tray_enabled_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=10)
        
        # Minimize to Tray
        self.minimize_to_tray_var = tk.BooleanVar(value=self.config.get("minimize_to_tray", True))
        tk.Checkbutton(
            container,
            text="⏬ Minimize to Tray on Close",
            variable=self.minimize_to_tray_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=10)
        
        # Auto-start
        self.autostart_var = tk.BooleanVar(value=self.config.get("autostart", False))
        tk.Checkbutton(
            container,
            text="🚀 Start with Windows (Not implemented yet)",
            variable=self.autostart_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            font=("Segoe UI", 10),
            state="disabled"
        ).pack(anchor="w", pady=10)
        
        # Notifications
        self.notifications_var = tk.BooleanVar(value=self.config.get("notifications_enabled", True))
        tk.Checkbutton(
            container,
            text="🔔 Enable Notifications",
            variable=self.notifications_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=10)
        
        # Show Resource Monitor
        self.show_resources_var = tk.BooleanVar(value=self.config.get("show_resources", True))
        tk.Checkbutton(
            container,
            text="📊 Show Resource Monitor",
            variable=self.show_resources_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=10)
    
    def setup_advanced_tab(self, parent):
        """Setup advanced settings tab"""
        container = tk.Frame(parent, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.grid_columnconfigure(1, weight=1)
        
        # Port Scan Timeout
        self.port_timeout_var = tk.DoubleVar(value=self.config.get("port_scan_timeout", 1.0))
        self.create_labeled_entry(
            container,
            "Port Scan Timeout (sec):",
            self.port_timeout_var,
            0
        )
        
        # ARP Timeout
        self.arp_timeout_var = tk.IntVar(value=self.config.get("arp_timeout", 2))
        self.create_labeled_entry(
            container,
            "ARP Timeout (sec):",
            self.arp_timeout_var,
            1
        )
        
        # UI Update Interval
        self.ui_update_var = tk.IntVar(value=self.config.get("ui_update_interval", 500))
        self.create_labeled_entry(
            container,
            "UI Update Interval (ms):",
            self.ui_update_var,
            2
        )
        
        # Warning
        warning = tk.Label(
            container,
            text="⚠️ Warning: Changing these values may affect stability",
            bg=self.colors["bg"],
            fg="#f9e2af",
            font=("Segoe UI", 9),
            wraplength=500
        )
        warning.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=20)
    
    def save_settings(self):
        """Save settings and close dialog"""
        try:
            # Update config
            self.config.update({
                "scan_interval": self.scan_interval_var.get(),
                "thread_pool_size": self.thread_pool_var.get(),
                "cache_size": self.cache_size_var.get(),
                "max_connections": self.max_conn_var.get(),
                "tray_enabled": self.tray_enabled_var.get(),
                "minimize_to_tray": self.minimize_to_tray_var.get(),
                "autostart": self.autostart_var.get(),
                "notifications_enabled": self.notifications_var.get(),
                "show_resources": self.show_resources_var.get(),
                "port_scan_timeout": self.port_timeout_var.get(),
                "arp_timeout": self.arp_timeout_var.get(),
                "ui_update_interval": self.ui_update_var.get()
            })
            
            # Save to file
            with open("config.json", "w") as f:
                json.dump(self.config, f, indent=4)
            
            # Callback
            if self.on_save:
                self.on_save(self.config)
            
            messagebox.showinfo("Settings", "Settings saved successfully!\nRestart may be required for some changes.")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    @staticmethod
    def load_config():
        """Load configuration from file"""
        default_config = {
            "scan_interval": 3,
            "thread_pool_size": 10,
            "cache_size": 1000,
            "max_connections": 50,
            "tray_enabled": True,
            "minimize_to_tray": True,
            "autostart": False,
            "notifications_enabled": True,
            "show_resources": True,
            "port_scan_timeout": 1.0,
            "arp_timeout": 2,
            "ui_update_interval": 500
        }
        
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except:
                pass
        
        return default_config
