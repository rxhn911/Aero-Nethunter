#!/usr/bin/env python3
"""
Modern Visual Components for Aero Nethunter
Glass morphism, gradients, and modern card designs
"""

import tkinter as tk
from tkinter import font as tkfont


class GlassCard(tk.Frame):
    """Glass morphism card widget"""
    
    def __init__(self, parent, colors=None, **kwargs):
        self.colors = colors or {}
        bg = self.colors.get("bg_card", "#1a1f3a")
        
        super().__init__(parent, bg=bg, **kwargs)
        
        # Create border effect
        self.config(highlightbackground=self.colors.get("accent", "#00d9ff"), 
                   highlightthickness=1, relief="flat")
        
    def add_content(self, content_widget):
        """Add content to the card"""
        content_widget.pack(fill="both", expand=True, padx=15, pady=15)


class GradientFrame(tk.Canvas):
    """Frame with gradient background"""
    
    def __init__(self, parent, color1, color2, direction="vertical", **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.direction = direction
        
        self.bind("<Configure>", self._draw_gradient)
    
    def _draw_gradient(self, event=None):
        """Draw gradient on canvas"""
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Parse colors
        r1, g1, b1 = self._hex_to_rgb(self.color1)
        r2, g2, b2 = self._hex_to_rgb(self.color2)
        
        # Draw gradient
        steps = height if self.direction == "vertical" else width
        
        for i in range(steps):
            ratio = i / steps
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            if self.direction == "vertical":
                self.create_line(0, i, width, i, fill=color, tags="gradient")
            else:
                self.create_line(i, 0, i, height, fill=color, tags="gradient")
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class ModernButton(tk.Canvas):
    """Modern button with gradient and shadow"""
    
    def __init__(self, parent, text, command=None, colors=None, width=200, height=45, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        
        self.colors = colors or {}
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        
        self.bg_color = self.colors.get("accent", "#00d9ff")
        self.hover_color = self.colors.get("accent_alt", "#ff2e97")
        self.is_hovered = False
        
        self.config(bg=self.colors.get("bg_main", "#0a0e27"))
        
        self._draw()
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _draw(self):
        """Draw button"""
        self.delete("all")
        
        # Shadow (using dark solid color instead of alpha)
        shadow_color = "#1a1a1a" if self.colors.get("bg_main", "#0a0e27") == "#0a0e27" else "#000000"
        self.create_oval(
            5, 8, self.width-5, self.height+5,
            fill=shadow_color, outline=""
        )
        
        # Button background with gradient effect
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # Main button
        self.create_rounded_rectangle(
            0, 0, self.width, self.height-5,
            radius=22, fill=color, outline=""
        )
        
        # Highlight (lighter overlay for 3D effect)
        # Using lighter version of the color instead of alpha
        highlight_color = self._lighten_color(color, 0.2)
        self.create_rounded_rectangle(
            2, 2, self.width-2, (self.height-5)//2,
            radius=20, fill=highlight_color, outline=""
        )
        
        # Text
        self.create_text(
            self.width/2, (self.height-5)/2,
            text=self.text, fill="#000000",
            font=("Segoe UI", 11, "bold")
        )
    
    def _lighten_color(self, hex_color, factor=0.2):
        """Lighten a hex color"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Create rounded rectangle"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_click(self, event):
        """Handle click"""
        if self.command:
            self.command()
    
    def _on_enter(self, event):
        """Handle hover enter"""
        self.is_hovered = True
        self._draw()
    
    def _on_leave(self, event):
        """Handle hover leave"""
        self.is_hovered = False
        self._draw()


class DeviceCard(tk.Frame):
    """Modern card for displaying device info"""
    
    def __init__(self, parent, device_info, colors=None, on_click=None):
        self.colors = colors or {}
        bg = self.colors.get("bg_card", "#1a1f3a")
        
        super().__init__(parent, bg=bg, relief="flat", bd=0)
        
        self.device_info = device_info
        self.on_click = on_click
        
        # Border
        self.config(highlightbackground=self.colors.get("accent", "#00d9ff"),
                   highlightthickness=1)
        
        self.setup_ui()
        
        # Hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        if on_click:
            self.bind("<Button-1>", lambda e: on_click(device_info))
    
    def setup_ui(self):
        """Setup card UI"""
        container = tk.Frame(self, bg=self.colors.get("bg_card"))
        container.pack(fill="both", expand=True, padx=15, pady=12)
        
        # Header with icon and IP
        header = tk.Frame(container, bg=self.colors.get("bg_card"))
        header.pack(fill="x", pady=(0, 8))
        
        # Device icon
        icon = self.device_info.get("type", "❓ Unknown").split()[0]
        tk.Label(
            header,
            text=icon,
            font=("Segoe UI", 20),
            bg=self.colors.get("bg_card")
        ).pack(side="left", padx=(0, 10))
        
        # IP address (main)
        tk.Label(
            header,
            text=self.device_info.get("ip", "Unknown"),
            font=("Segoe UI", 14, "bold"),
            bg=self.colors.get("bg_card"),
            fg=self.colors.get("accent", "#00d9ff")
        ).pack(side="left")
        
        # Status badge
        if not self.device_info.get("is_known", False):
            badge = tk.Label(
                header,
                text="NEW",
                font=("Segoe UI", 8, "bold"),
                bg=self.colors.get("err", "#ff4757"),
                fg="#000000",
                padx=6,
                pady=2
            )
            badge.pack(side="right")
        
        # Separator
        sep = tk.Frame(container, bg=self.colors.get("accent", "#00d9ff"), height=1)
        sep.pack(fill="x", pady=8)
        
        # Info grid
        info_frame = tk.Frame(container, bg=self.colors.get("bg_card"))
        info_frame.pack(fill="x")
        
        # Vendor
        self._add_info_row(info_frame, "Vendor:", 
                          self.device_info.get("vendor", "Unknown"), 0)
        
        # MAC
        self._add_info_row(info_frame, "MAC:", 
                          self.device_info.get("mac", "Unknown"), 1)
        
        # Hostname
        self._add_info_row(info_frame, "Host:", 
                          self.device_info.get("host", "?"), 2)
        
        # Ports (if any)
        ports = self.device_info.get("ports", "")
        if ports:
            self._add_info_row(info_frame, "Ports:", 
                              ports[:30] + "..." if len(ports) > 30 else ports, 3)
    
    def _add_info_row(self, parent, label, value, row):
        """Add info row"""
        tk.Label(
            parent,
            text=label,
            font=("Segoe UI", 9),
            bg=self.colors.get("bg_card"),
            fg=self.colors.get("text_dim", "#8892b0"),
            anchor="w"
        ).grid(row=row, column=0, sticky="w", pady=2, padx=(0, 10))
        
        tk.Label(
            parent,
            text=value,
            font=("Consolas", 9),
            bg=self.colors.get("bg_card"),
            fg=self.colors.get("text", "#ffffff"),
            anchor="w"
        ).grid(row=row, column=1, sticky="w", pady=2)
    
    def _on_enter(self, event):
        """Hover effect"""
        self.config(bg=self.colors.get("hover", "#1e2541"),
                   highlightbackground=self.colors.get("accent_alt", "#ff2e97"),
                   highlightthickness=2)
        for child in self.winfo_children():
            try:
                child.config(bg=self.colors.get("hover", "#1e2541"))
            except:
                pass
    
    def _on_leave(self, event):
        """Remove hover effect"""
        bg = self.colors.get("bg_card", "#1a1f3a")
        self.config(bg=bg,
                   highlightbackground=self.colors.get("accent", "#00d9ff"),
                   highlightthickness=1)
        for child in self.winfo_children():
            try:
                child.config(bg=bg)
            except:
                pass


class Badge(tk.Label):
    """Small badge for status indicators"""
    
    def __init__(self, parent, text, badge_type="info", colors=None):
        self.colors = colors or {}
  
        type_colors = {
            "info": colors.get("accent", "#00d9ff") if colors else "#00d9ff",
            "success": colors.get("success", "#00ff88") if colors else "#00ff88",
            "warning": colors.get("warn", "#ffaa00") if colors else "#ffaa00",
            "error": colors.get("err", "#ff4757") if colors else "#ff4757"
        }
        
        bg_color = type_colors.get(badge_type, type_colors["info"])
        
        super().__init__(
            parent,
            text=text,
            font=("Segoe UI", 8, "bold"),
            bg=bg_color,
            fg="#000000",
            padx=8,
            pady=3,
            relief="flat"
        )
