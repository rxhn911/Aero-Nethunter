#!/usr/bin/env python3
"""
System Tray Manager for Aero Nethunter
Handles system tray icon, notifications, and background mode
"""

import pystray
from PIL import Image, ImageDraw
import threading
from tkinter import messagebox


class TrayManager:
    """System tray integration manager"""
    
    def __init__(self, app_name="Aero Nethunter", on_show=None, on_hide=None, 
                 on_quick_scan=None, on_exit=None):
        """
        Initialize tray manager
        Args:
            app_name: Application name
            on_show: Callback when "Show" is clicked
            on_hide: Callback when "Hide" is clicked
            on_quick_scan: Callback when "Quick Scan" is clicked
            on_exit: Callback when "Exit" is clicked
        """
        self.app_name = app_name
        self.on_show = on_show
        self.on_hide = on_hide
        self.on_quick_scan = on_quick_scan
        self.on_exit = on_exit
        
        self.icon = None
        self.visible = False
        self.tray_thread = None
        
    def create_icon_image(self):
        """Create a simple icon image"""
        # Create a 64x64 image with transparent background
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Draw a network-like icon (circle with lines)
        # Outer circle (blue)
        dc.ellipse([8, 8, 56, 56], fill=(137, 180, 250, 255), outline=(137, 180, 250, 255))
        
        # Inner circle (dark)
        dc.ellipse([20, 20, 44, 44], fill=(30, 30, 46, 255), outline=(30, 30, 46, 255))
        
        # Network nodes (small circles)
        node_color = (166, 227, 161, 255)
        dc.ellipse([28, 12, 36, 20], fill=node_color)  # Top
        dc.ellipse([12, 28, 20, 36], fill=node_color)  # Left
        dc.ellipse([44, 28, 52, 36], fill=node_color)  # Right
        dc.ellipse([28, 44, 36, 52], fill=node_color)  # Bottom
        
        return image
    
    def create_menu(self):
        """Create tray menu"""
        return pystray.Menu(
            pystray.MenuItem(
                "📊 Show Dashboard", 
                self._on_show_clicked, 
                default=True,
                visible=lambda item: not self.visible
            ),
            pystray.MenuItem(
                "🔍 Quick Scan", 
                self._on_quick_scan_clicked
            ),
            pystray.MenuItem(
                "⏸ Hide to Tray", 
                self._on_hide_clicked,
                visible=lambda item: self.visible
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "🚪 Exit", 
                self._on_exit_clicked
            )
        )
    
    def _on_show_clicked(self, icon, item):
        """Handle show menu click"""
        if self.on_show:
            self.on_show()
        self.visible = True
        self.icon.update_menu()
    
    def _on_hide_clicked(self, icon, item):
        """Handle hide menu click"""
        if self.on_hide:
            self.on_hide()
        self.visible = False
        self.icon.update_menu()
    
    def _on_quick_scan_clicked(self, icon, item):
        """Handle quick scan menu click"""
        if self.on_quick_scan:
            self.on_quick_scan()
            self.notify("Quick Scan Started", "Network scan initiated from tray")
    
    def _on_exit_clicked(self, icon, item):
        """Handle exit menu click"""
        if self.on_exit:
            self.on_exit()
        self.stop()
    
    def start(self):
        """Start system tray icon"""
        if self.icon is not None:
            return  # Already running
        
        image = self.create_icon_image()
        menu = self.create_menu()
        
        self.icon = pystray.Icon(
            self.app_name,
            image,
            self.app_name,
            menu
        )
        
        # Run in separate thread
        self.tray_thread = threading.Thread(target=self._run_icon, daemon=True)
        self.tray_thread.start()
    
    def _run_icon(self):
        """Run the icon (blocking)"""
        try:
            self.icon.run()
        except Exception as e:
            print(f"[Tray] Error: {e}")
    
    def stop(self):
        """Stop system tray icon"""
        if self.icon:
            self.icon.stop()
            self.icon = None
    
    def notify(self, title, message):
        """Show a notification balloon"""
        if self.icon and self.icon.HAS_NOTIFICATION:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                print(f"[Tray] Notification error: {e}")
    
    def update_tooltip(self, text):
        """Update tray icon tooltip"""
        if self.icon:
            self.icon.title = text
    
    def set_visible_state(self, visible):
        """Update visible state"""
        self.visible = visible
        if self.icon:
            self.icon.update_menu()


class TrayNotificationManager:
    """Manages notifications with rate limiting"""
    
    def __init__(self, tray_manager, min_interval=5):
        """
        Initialize notification manager
        Args:
            tray_manager: TrayManager instance
            min_interval: Minimum seconds between same notifications
        """
        self.tray = tray_manager
        self.min_interval = min_interval
        self.last_notifications = {}
        
    def notify_new_device(self, device_info):
        """Notify about new device"""
        import time
        
        # Rate limiting
        key = "new_device"
        current_time = time.time()
        if key in self.last_notifications:
            if current_time - self.last_notifications[key] < self.min_interval:
                return  # Skip notification
        
        self.last_notifications[key] = current_time
        
        ip = device_info.get("ip", "Unknown")
        vendor = device_info.get("vendor", "Unknown")
        
        self.tray.notify(
            "New Device Detected",
            f"IP: {ip}\nVendor: {vendor}"
        )
    
    def notify_scan_complete(self, device_count):
        """Notify about scan completion"""
        import time
        
        key = "scan_complete"
        current_time = time.time()
        if key in self.last_notifications:
            if current_time - self.last_notifications[key] < self.min_interval:
                return
        
        self.last_notifications[key] = current_time
        
        self.tray.notify(
            "Scan Complete",
            f"Found {device_count} device(s)"
        )
    
    def notify_suspicious_activity(self, message):
        """Notify about suspicious activity"""
        self.tray.notify(
            "⚠️ Alert",
            message
        )


def create_tray_manager(app_instance):
    """
    Helper function to create tray manager for GUI application
    Args:
        app_instance: Instance of main GUI application
    Returns:
        TrayManager instance
    """
    def on_show():
        app_instance.root.deiconify()
        app_instance.root.lift()
        app_instance.root.focus_force()
    
    def on_hide():
        app_instance.root.withdraw()
    
    def on_quick_scan():
        if not app_instance.scanning:
            app_instance.toggle_scan()
    
    def on_exit():
        app_instance.root.quit()
    
    return TrayManager(
        app_name="Aero Nethunter",
        on_show=on_show,
        on_hide=on_hide,
        on_quick_scan=on_quick_scan,
        on_exit=on_exit
    )
