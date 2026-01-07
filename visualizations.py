#!/usr/bin/env python3
"""
Data Visualization Module for Aero Nethunter
Real-time graphs and statistics
"""

import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import time


class TrafficGraph:
    """Real-time traffic monitoring graph"""
    
    def __init__(self, parent, colors=None, max_points=60):
        self.parent = parent
        self.colors = colors or {}
        self.max_points = max_points
        
        # Data storage
        self.timestamps = deque(maxlen=max_points)
        self.download_data = deque(maxlen=max_points)
        self.upload_data = deque(maxlen=max_points)
        
        # Initialize with zeros
        for _ in range(max_points):
            self.timestamps.append(0)
            self.download_data.append(0)
            self.upload_data.append(0)
        
        self.setup_graph()
    
    def setup_graph(self):
        """Setup matplotlib graph"""
        # Create figure with dark background
        bg_color = self.colors.get("bg_card", "#1a1f3a")
        text_color = self.colors.get("text", "#ffffff")
        
        self.figure = Figure(figsize=(6, 3), facecolor=bg_color)
        self.ax = self.figure.add_subplot(111)
        
        # Style
        self.ax.set_facecolor(self.colors.get("bg_main", "#0a0e27"))
        self.ax.spines['bottom'].set_color(text_color)
        self.ax.spines['top'].set_color(bg_color) 
        self.ax.spines['right'].set_color(bg_color)
        self.ax.spines['left'].set_color(text_color)
        self.ax.tick_params(colors=text_color, which='both')
        
        # Labels
        self.ax.set_xlabel('Time (seconds)', color=text_color, fontsize=9)
        self.ax.set_ylabel('Traffic (KB/s)', color=text_color, fontsize=9)
        self.ax.set_title('Network Traffic', color=self.colors.get("accent", "#00d9ff"), 
                         fontsize=11, fontweight='bold', pad=10)
        
        # Initial empty lines
        self.download_line, = self.ax.plot(
            [], [], 
            color=self.colors.get("accent", "#00d9ff"),
            linewidth=2,
            label='↓ Download'
        )
        self.upload_line, = self.ax.plot(
            [], [],
            color=self.colors.get("accent_alt", "#ff2e97"),
            linewidth=2,
            label='↑ Upload'
        )
        
        # Legend
        self.ax.legend(loc='upper left', framealpha=0.8, facecolor=bg_color, 
                      edgecolor=text_color, fontsize=8)
        
        # Grid
        self.ax.grid(True, alpha=0.2, color=text_color, linestyle='--', linewidth=0.5)
        
        # Tight layout
        self.figure.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def update(self, download_kb, upload_kb):
        """Update graph with new data point"""
        current_time = time.time()
        
        # Add new data
        if not self.timestamps or current_time - self.timestamps[-1] >= 1:
            self.timestamps.append(current_time)
            self.download_data.append(download_kb)
            self.upload_data.append(upload_kb)
        else:
            # Update current second
            self.download_data[-1] = download_kb
            self.upload_data[-1] = upload_kb
        
        # Calculate relative timestamps
        if self.timestamps:
            base_time = self.timestamps[0]
            times = [t - base_time for t in self.timestamps]
        else:
            times = list(range(len(self.download_data)))
        
        # Update lines
        self.download_line.set_data(times, list(self.download_data))
        self.upload_line.set_data(times, list(self.upload_data))
        
        # Auto-scale
        self.ax.relim()
        self.ax.autoscale_view()
        
        # Set x-axis limits
        if times:
            self.ax.set_xlim(max(0, times[-1] - 60), times[-1] + 1)
        
        # Redraw
        try:
            self.canvas.draw_idle()
        except:
            pass
    
    def clear(self):
        """Clear graph data"""
        self.timestamps.clear()
        self.download_data.clear()
        self.upload_data.clear()
        
        for _ in range(self.max_points):
            self.timestamps.append(0)
            self.download_data.append(0)
            self.upload_data.append(0)
        
        self.update(0, 0)


class DeviceTypePieChart:
    """Pie chart showing device type distribution"""
    
    def __init__(self, parent, colors=None):
        self.parent = parent
        self.colors = colors or {}
        self.setup_chart()
    
    def setup_chart(self):
        """Setup pie chart"""
        bg_color = self.colors.get("bg_card", "#1a1f3a")
        text_color = self.colors.get("text", "#ffffff")
        
        self.figure = Figure(figsize=(4, 4), facecolor=bg_color)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(bg_color)
        
        # Title
        self.ax.set_title('Device Types', color=self.colors.get("accent", "#00d9ff"),
                         fontsize=11, fontweight='bold')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def update(self, device_counts):
        """
        Update pie chart
        Args:
            device_counts: Dict like {"Mobile": 5, "PC": 3, "Router": 1}
        """
        self.ax.clear()
        
        if not device_counts or sum(device_counts.values()) == 0:
            self.ax.text(0.5, 0.5, 'No devices', ha='center', va='center',
                        transform=self.ax.transAxes, color=self.colors.get("text_dim"),
                        fontsize=12)
            self.canvas.draw_idle()
            return
        
        labels = list(device_counts.keys())
        sizes = list(device_counts.values())
        
        # Colors for each type
        type_colors = {
            "Mobile": self.colors.get("accent", "#00d9ff"),
            "PC": self.colors.get("accent_alt", "#ff2e97"),
            "Router": self.colors.get("success", "#00ff88"),
            "Unknown": self.colors.get("text_dim", "#8892b0")
        }
        
        slice_colors = [type_colors.get(label.split()[-1], "#888888") for label in labels]
        
        # Create pie chart
        wedges, texts, autotexts = self.ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=slice_colors,
            textprops={'color': self.colors.get("text", "#ffffff"), 'fontsize': 9}
        )
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)
        
        self.ax.set_title('Device Types', color=self.colors.get("accent", "#00d9ff"),
                         fontsize=11, fontweight='bold')
        
        self.canvas.draw_idle()


class StatsDashboard(tk.Frame):
    """Dashboard with multiple statistics"""
    
    def __init__(self, parent, colors=None):
        bg = colors.get("bg_card", "#1a1f3a") if colors else "#1a1f3a"
        super().__init__(parent, bg=bg)
        
        self.colors = colors or {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dashboard UI"""
        bg = self.colors.get("bg_card", "#1a1f3a")
        
        # Title
        tk.Label(
            self,
            text="📊 Statistics Dashboard",
            font=("Segoe UI", 14, "bold"),
            bg=bg,
            fg=self.colors.get("accent", "#00d9ff")
        ).pack(pady=15)
        
        # Stats grid
        stats_frame = tk.Frame(self, bg=bg)
        stats_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create stat items
        self.stat_labels = {}
        
        stats = [
            ("total_devices", "Total Devices", "🖥️"),
            ("active_scans", "Active Scans", "🔍"),
            ("total_ports", "Open Ports", "🔓"),
            ("total_traffic", "Total Traffic", "📶"),
            ("avg_response", "Avg Response", "⚡"),
            ("cache_hits", "Cache Hits", "💾")
        ]
        
        row = 0
        col = 0
        for key, label, icon in stats:
            item_frame = tk.Frame(stats_frame, bg=self.colors.get("bg_main", "#0a0e27"))
            item_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            
            # Icon
            tk.Label(
                item_frame,
                text=icon,
                font=("Segoe UI", 20),
                bg=self.colors.get("bg_main"),
                fg=self.colors.get("accent")
            ).pack(pady=(10, 5))
            
            # Value
            value_label = tk.Label(
                item_frame,
                text="0",
                font=("Segoe UI", 18, "bold"),
                bg=self.colors.get("bg_main"),
                fg=self.colors.get("text")
            )
            value_label.pack()
            self.stat_labels[key] = value_label
            
            # Label
            tk.Label(
                item_frame,
                text=label,
                font=("Segoe UI", 8),
                bg=self.colors.get("bg_main"),
                fg=self.colors.get("text_dim")
            ).pack(pady=(0, 10))
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        # Configure grid
        for i in range(2):
            stats_frame.grid_columnconfigure(i, weight=1)
    
    def update_stat(self, key, value):
        """Update a specific stat"""
        if key in self.stat_labels:
            self.stat_labels[key].config(text=str(value))
    
    def update_all(self, stats_dict):
        """Update all stats from dictionary"""
        for key, value in stats_dict.items():
            self.update_stat(key, value)


class MiniGraph(tk.Canvas):
    """Mini line graph for inline stats"""
    
    def __init__(self, parent, width=100, height=30, colors=None, max_points=20):
        super().__init__(parent, width=width, height=height, highlightthickness=0)
        
        self.colors = colors or {}
        self.width = width
        self.height = height
        self.max_points = max_points
        self.data = deque(maxlen=max_points)
        
        bg = colors.get("bg_card", "#1a1f3a") if colors else "#1a1f3a"
        self.config(bg=bg)
        
        # Initialize with zeros
        for _ in range(max_points):
            self.data.append(0)
    
    def update(self, value):
        """Add new data point and redraw"""
        self.data.append(value)
        self._draw()
    
    def _draw(self):
        """Draw the mini graph"""
        self.delete("all")
        
        if not self.data or len(self.data) < 2:
            return
        
        # Normalize data to height
        data_list = list(self.data)
        max_val = max(data_list) if max(data_list) > 0 else 1
        
        points = []
        step = self.width / (len(data_list) - 1)
        
        for i, val in enumerate(data_list):
            x = i * step
            y = self.height - (val / max_val * self.height * 0.9)
            points.append((x, y))
        
        # Draw line
        if len(points) >= 2:
            self.create_line(
                points,
                fill=self.colors.get("accent", "#00d9ff"),
                width=2,
                smooth=True
            )
            
            # Fill area under line
            fill_points = [(0, self.height)] + points + [(self.width, self.height)]
            self.create_polygon(
                fill_points,
                fill=self.colors.get("accent", "#00d9ff"),
                stipple="gray50",
                outline=""
            )
