#!/usr/bin/env python3
"""
UI Components for Aero Nethunter
Modern, interactive UI elements
"""

import tkinter as tk
from tkinter import ttk
import time


class SearchFilterPanel(tk.Frame):
    """Search and filter panel for devices"""
    
    def __init__(self, parent, on_search=None, on_filter=None, colors=None):
        super().__init__(parent, bg=colors.get("bg_card", "#1a1f3a"))
        self.on_search = on_search
        self.on_filter = on_filter
        self.colors = colors or {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup search and filter UI"""
        # Search box
        search_frame = tk.Frame(self, bg=self.colors.get("bg_card"))
        search_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            search_frame,
            text="🔍",
            font=("Segoe UI", 14),
            bg=self.colors.get("bg_card"),
            fg=self.colors.get("text")
        ).pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._on_search_change())
        
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=self.colors.get("bg_main", "#0a0e27"),
            fg=self.colors.get("text", "white"),
            relief="flat",
            font=("Segoe UI", 11),
            insertbackground=self.colors.get("accent", "#00d9ff")
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.insert(0, "Search IP, MAC, or Vendor...")
        self.search_entry.bind("<FocusIn>", self._on_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_focus_out)
        
        # Filter options
        filter_frame = tk.Frame(self, bg=self.colors.get("bg_card"))
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Label(
            filter_frame,
            text="Filter:",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors.get("bg_card"),
            fg=self.colors.get("text_dim")
        ).pack(side="left", padx=(0, 10))
        
        # Filter checkboxes
        self.filter_vars = {}
        filters = [
            ("new", "New Only"),
            ("mobile", "📱 Mobile"),
            ("pc", "💻 PC"),
            ("router", "🌐 Router")
        ]
        
        for key, label in filters:
            var = tk.BooleanVar(value=False)
            var.trace("w", lambda *args: self._on_filter_change())
            self.filter_vars[key] = var
            
            cb = tk.Checkbutton(
                filter_frame,
                text=label,
                variable=var,
                bg=self.colors.get("bg_card"),
                fg=self.colors.get("text_dim"),
                selectcolor=self.colors.get("bg_main"),
                activebackground=self.colors.get("bg_card"),
                font=("Segoe UI", 9)
            )
            cb.pack(side="left", padx=5)
    
    def _on_focus_in(self, event):
        """Clear placeholder on focus"""
        if self.search_entry.get() == "Search IP, MAC, or Vendor...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.colors.get("text"))
    
    def _on_focus_out(self, event):
        """Restore placeholder if empty"""
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search IP, MAC, or Vendor...")
            self.search_entry.config(fg=self.colors.get("text_dim"))
    
    def _on_search_change(self):
        """Handle search text change"""
        if self.on_search:
            query = self.search_var.get()
            if query != "Search IP, MAC, or Vendor...":
                self.on_search(query)
    
    def _on_filter_change(self):
        """Handle filter change"""
        if self.on_filter:
            active_filters = {k: v.get() for k, v in self.filter_vars.items()}
            self.on_filter(active_filters)
    
    def get_search_query(self):
        """Get current search query"""
        query = self.search_var.get()
        return query if query != "Search IP, MAC, or Vendor..." else ""
    
    def get_active_filters(self):
        """Get active filters"""
        return {k: v.get() for k, v in self.filter_vars.items() if v.get()}


class ToastNotification:
    """Toast notification system"""
    
    def __init__(self, parent, colors=None):
        self.parent = parent
        self.colors = colors or {}
        self.notifications = []
        self.y_offset = 10
    
    def show(self, message, type="info", duration=3000, action=None):
        """
        Show a toast notification
        Args:
            message: Notification message
            type: Type (success, warning, error, info)
            duration: Duration in milliseconds
            action: Optional action callback
        """
        # Create toast window
        toast = tk.Toplevel(self.parent)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        
        # Set color based on type
        type_colors = {
            "success": self.colors.get("success", "#00ff88"),
            "warning": self.colors.get("warn", "#ffaa00"),
            "error": self.colors.get("err", "#ff4757"),
            "info": self.colors.get("accent", "#00d9ff")
        }
        bg_color = type_colors.get(type, type_colors["info"])
        
        # Icon based on type
        icons = {
            "success": "✓",
            "warning": "⚠",
            "error": "✕",
            "info": "ℹ"
        }
        icon = icons.get(type, icons["info"])
        
        # Content frame
        frame = tk.Frame(toast, bg=bg_color, relief="flat")
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Icon
        tk.Label(
            frame,
            text=icon,
            font=("Segoe UI", 16, "bold"),
            bg=bg_color,
            fg="#000000"
        ).pack(side="left", padx=(10, 5), pady=10)
        
        # Message
        tk.Label(
            frame,
            text=message,
            font=("Segoe UI", 10),
            bg=bg_color,
            fg="#000000",
            wraplength=250
        ).pack(side="left", padx=(0, 10), pady=10)
        
        # Action button (if provided)
        if action:
            btn = tk.Button(
                frame,
                text="Action",
                command=lambda: self._on_action(toast, action),
                bg="#ffffff",
                fg="#000000",
                relief="flat",
                font=("Segoe UI", 9, "bold"),
                cursor="hand2"
            )
            btn.pack(side="right", padx=10, pady=10)
        
        # Position toast
        toast.update_idletasks()
        width = toast.winfo_width()
        height = toast.winfo_height()
        
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        
        x = screen_width - width - 20
        y = self.y_offset
        
        toast.geometry(f"+{x}+{y}")
        
        # Track notification
        self.notifications.append(toast)
        self.y_offset += height + 10
        
        # Slide in animation
        self._animate_slide_in(toast, x, y)
        
        # Auto dismiss
        if duration > 0:
            toast.after(duration, lambda: self._dismiss(toast))
    
    def _animate_slide_in(self, toast, target_x, target_y, steps=10):
        """Animate toast sliding in"""
        start_x = self.parent.winfo_screenwidth()
        
        def step(i):
            if i <= steps:
                progress = i / steps
                current_x = int(start_x + (target_x - start_x) * progress)
                toast.geometry(f"+{current_x}+{target_y}")
                toast.after(20, lambda: step(i + 1))
        
        step(0)
    
    def _on_action(self, toast, action):
        """Handle action button click"""
        self._dismiss(toast)
        if action:
            action()
    
    def _dismiss(self, toast):
        """Dismiss a toast notification"""
        # Fade out animation
        self._animate_fade_out(toast)
        
        if toast in self.notifications:
            self.notifications.remove(toast)
            
            # Adjust positions of remaining toasts
            self.y_offset = 10
            for t in self.notifications:
                t.geometry(f"+{t.winfo_x()}+{self.y_offset}")
                self.y_offset += t.winfo_height() + 10
    
    def _animate_fade_out(self, toast):
        """Animate toast fading out"""
        try:
            alpha = 1.0
            def fade(a):
                if a > 0:
                    toast.attributes('-alpha', a)
                    toast.after(30, lambda: fade(a - 0.1))
                else:
                    toast.destroy()
            fade(alpha)
        except:
            toast.destroy()


class StatCard(tk.Frame):
    """Stat card widget"""
    
    def __init__(self, parent, title, value="0", icon="📊", colors=None):
        bg = colors.get("bg_card", "#1a1f3a") if colors else "#1a1f3a"
        super().__init__(parent, bg=bg, relief="flat", bd=0)
        
        self.colors = colors or {}
        self.value_var = tk.StringVar(value=str(value))
        
        # Content
        container = tk.Frame(self, bg=bg)
        container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Icon
        tk.Label(
            container,
            text=icon,
            font=("Segoe UI", 24),
            bg=bg
        ).pack(anchor="w")
        
        # Value
        self.value_label = tk.Label(
            container,
            textvariable=self.value_var,
            font=("Segoe UI", 28, "bold"),
            bg=bg,
            fg=colors.get("accent", "#00d9ff") if colors else "#00d9ff"
        )
        self.value_label.pack(anchor="w", pady=(5, 0))
        
        # Title
        tk.Label(
            container,
            text=title,
            font=("Segoe UI", 10),
            bg=bg,
            fg=colors.get("text_dim", "#8892b0") if colors else "#8892b0"
        ).pack(anchor="w")
        
        # Hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        for child in self.winfo_children():
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)
    
    def update_value(self, value, animated=True):
        """Update stat value with optional animation"""
        if animated:
            try:
                current = int(self.value_var.get().replace(",", ""))
                target = int(value)
                self._animate_count(current, target)
            except:
                self.value_var.set(str(value))
        else:
            self.value_var.set(str(value))
    
    def _animate_count(self, start, end, steps=20):
        """Animate number counting"""
        step_value = (end - start) / steps
        
        def count(i, current):
            if i < steps:
                current += step_value
                self.value_var.set(f"{int(current):,}")
                self.after(30, lambda: count(i + 1, current))
            else:
                self.value_var.set(f"{end:,}")
        
        count(0, start)
    
    def _on_enter(self, event):
        """Hover enter effect"""
        self.config(bg=self.colors.get("hover", "#1e2541"))
        for child in self.winfo_children():
            try:
                child.config(bg=self.colors.get("hover", "#1e2541"))
            except:
                pass
    
    def _on_leave(self, event):
        """Hover leave effect"""
        bg = self.colors.get("bg_card", "#1a1f3a")
        self.config(bg=bg)
        for child in self.winfo_children():
            try:
                child.config(bg=bg)
            except:
                pass


class AnimatedButton(tk.Button):
    """Button with hover animation"""
    
    def __init__(self, parent, text, command=None, colors=None, **kwargs):
        self.colors = colors or {}
        self.default_bg = kwargs.pop("bg", colors.get("accent", "#00d9ff") if colors else "#00d9ff")
        self.hover_bg = self.colors.get("accent_alt", "#ff2e97")
        
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=self.default_bg,
            fg=kwargs.pop("fg", "#000000"),
            relief="flat",
            cursor="hand2",
            font=kwargs.pop("font", ("Segoe UI", 11, "bold")),
            **kwargs
        )
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Hover enter"""
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        """Hover leave"""
        self.config(bg=self.default_bg)


class ProgressBar(tk.Canvas):
    """Animated progress bar"""
    
    def __init__(self, parent, width=200, height=20, colors=None):
        super().__init__(parent, width=width, height=height, highlightthickness=0)
        
        self.colors = colors or {}
        self.width = width
        self.height = height
        self.progress = 0
        
        bg = colors.get("bg_card", "#1a1f3a") if colors else "#1a1f3a"
        self.config(bg=bg)
        
        # Background
        self.create_rectangle(
            0, 0, width, height,
            fill=colors.get("bg_main", "#0a0e27") if colors else "#0a0e27",
            outline=""
        )
        
        # Progress bar
        self.bar = self.create_rectangle(
            0, 0, 0, height,
            fill=colors.get("accent", "#00d9ff") if colors else "#00d9ff",
            outline=""
        )
    
    def set_progress(self, percent, animated=True):
        """Set progress (0-100)"""
        target_width = (percent / 100) * self.width
        
        if animated:
            self._animate_to(target_width)
        else:
            self.coords(self.bar, 0, 0, target_width, self.height)
            self.progress = percent
    
    def _animate_to(self, target_width, steps=10):
        """Animate progress bar"""
        current_width = (self.progress / 100) * self.width
        step = (target_width - current_width) / steps
        
        def animate(i, width):
            if i < steps:
                width += step
                self.coords(self.bar, 0, 0, width, self.height)
                self.after(20, lambda: animate(i + 1, width))
            else:
                self.coords(self.bar, 0, 0, target_width, self.height)
                self.progress = (target_width / self.width) * 100
        
        animate(0, current_width)
