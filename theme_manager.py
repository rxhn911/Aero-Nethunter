#!/usr/bin/env python3
"""
Theme Manager for Aero Nethunter
Handles multiple color themes and visual preferences
"""

import json
import os


class Theme:
    """Theme configuration class"""
    
    def __init__(self, name, colors, fonts=None, effects=None):
        self.name = name
        self.colors = colors
        self.fonts = fonts or self.default_fonts()
        self.effects = effects or self.default_effects()
    
    @staticmethod
    def default_fonts():
        return {
            "title": ("Segoe UI", 24, "bold"),
            "heading": ("Segoe UI", 14, "bold"),
            "body": ("Segoe UI", 10),
            "mono": ("Consolas", 10),
            "button": ("Segoe UI", 11, "bold")
        }
    
    @staticmethod
    def default_effects():
        return {
            "animations": True,
            "shadows": True,
            "hover_effects": True,
            "transitions": True
        }
    
    def to_dict(self):
        """Convert theme to dictionary"""
        return {
            "name": self.name,
            "colors": self.colors,
            "fonts": self.fonts,
            "effects": self.effects
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create theme from dictionary"""
        return cls(
            name=data["name"],
            colors=data["colors"],
            fonts=data.get("fonts"),
            effects=data.get("effects")
        )


class ThemeManager:
    """Manages application themes"""
    
    # Preset themes
    THEMES = {
        "cyberpunk": Theme(
            name="Cyberpunk",
            colors={
                "bg_main": "#0a0e27",
                "bg_side": "#060818",
                "bg_card": "#1a1f3a",
                "accent": "#00d9ff",
                "accent_alt": "#ff2e97",
                "text": "#ffffff",
                "text_dim": "#8892b0",
                "success": "#00ff88",
                "warn": "#ffaa00",
                "err": "#ff4757",
                "hover": "#1e2541"
            }
        ),
        
        "ocean": Theme(
            name="Ocean",
            colors={
                "bg_main": "#0a1929",
                "bg_side": "#001e3c",
                "bg_card": "#132f4c",
                "accent": "#3d9ff7",
                "accent_alt": "#29b6f6",
                "text": "#ffffff",
                "text_dim": "#90caf9",
                "success": "#4caf50",
                "warn": "#ff9800",
                "err": "#f44336",
                "hover": "#1e4976"
            }
        ),
        
        "forest": Theme(
            name="Forest",
            colors={
                "bg_main": "#0d1b0d",
                "bg_side": "#071207",
                "bg_card": "#1a2f1a",
                "accent": "#4caf50",
                "accent_alt": "#8bc34a",
                "text": "#e8f5e9",
                "text_dim": "#a5d6a7",
                "success": "#66bb6a",
                "warn": "#ffa726",
                "err": "#ef5350",
                "hover": "#2e4a2e"
            }
        ),
        
        "sunset": Theme(
            name="Sunset",
            colors={
                "bg_main": "#1a0f1f",
                "bg_side": "#0f0514",
                "bg_card": "#2d1b3d",
                "accent": "#ff6b6b",
                "accent_alt": "#feca57",
                "text": "#fff0f6",
                "text_dim": "#f8b4d9",
                "success": "#48dbfb",
                "warn": "#ff9ff3",
                "err": "#ff6348",
                "hover": "#3d2550"
            }
        ),
        
        "hacker": Theme(
            name="Hacker Terminal",
            colors={
                "bg_main": "#000000",
                "bg_side": "#0a0a0a",
                "bg_card": "#1a1a1a",
                "accent": "#00ff00",
                "accent_alt": "#00cc00",
                "text": "#00ff00",
                "text_dim": "#00aa00",
                "success": "#00ff00",
                "warn": "#ffff00",
                "err": "#ff0000",
                "hover": "#1a3d1a"
            }
        ),
        
        "dark": Theme(
            name="Dark (Classic)",
            colors={
                "bg_main": "#1e1e2e",
                "bg_side": "#11111b",
                "bg_card": "#313244",
                "accent": "#89b4fa",
                "accent_alt": "#cba6f7",
                "text": "#cdd6f4",
                "text_dim": "#9399b2",
                "success": "#a6e3a1",
                "warn": "#f9e2af",
                "err": "#f38ba8",
                "hover": "#45475a"
            }
        ),
        
        "light": Theme(
            name="Light",
            colors={
                "bg_main": "#eff1f5",
                "bg_side": "#e6e9ef",
                "bg_card": "#dce0e8",
                "accent": "#1e66f5",
                "accent_alt": "#8839ef",
                "text": "#4c4f69",
                "text_dim": "#6c6f85",
                "success": "#40a02b",
                "warn": "#df8e1d",
                "err": "#d20f39",
                "hover": "#ccd0da"
            }
        )
    }
    
    def __init__(self, config_file="theme_config.json"):
        self.config_file = config_file
        self.current_theme = None
        self.custom_themes = {}
        self.callbacks = []  # Theme change callbacks
        
        self.load_config()
    
    def load_config(self):
        """Load theme configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load current theme
                    theme_name = data.get("current_theme", "cyberpunk")
                    if theme_name in self.THEMES:
                        self.current_theme = self.THEMES[theme_name]
                    elif theme_name in self.custom_themes:
                        self.current_theme = self.custom_themes[theme_name]
                    else:
                        self.current_theme = self.THEMES["cyberpunk"]
                    
                    # Load custom themes
                    for custom in data.get("custom_themes", []):
                        theme = Theme.from_dict(custom)
                        self.custom_themes[theme.name.lower()] = theme
                        
            except Exception as e:
                print(f"[Theme] Error loading config: {e}")
                self.current_theme = self.THEMES["cyberpunk"]
        else:
            self.current_theme = self.THEMES["cyberpunk"]
    
    def save_config(self):
        """Save theme configuration to file"""
        try:
            data = {
                "current_theme": self.current_theme.name.lower().replace(" ", "_"),
                "custom_themes": [t.to_dict() for t in self.custom_themes.values()]
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[Theme] Error saving config: {e}")
    
    def get_theme(self, theme_name=None):
        """Get theme by name or current theme"""
        if theme_name is None:
            return self.current_theme
        
        theme_key = theme_name.lower().replace(" ", "_")
        if theme_key in self.THEMES:
            return self.THEMES[theme_key]
        elif theme_key in self.custom_themes:
            return self.custom_themes[theme_key]
        
        return self.current_theme
    
    def set_theme(self, theme_name):
        """Set current theme and notify callbacks"""
        theme = self.get_theme(theme_name)
        if theme:
            self.current_theme = theme
            self.save_config()
            
            # Notify all registered callbacks
            for callback in self.callbacks:
                try:
                    callback(theme)
                except Exception as e:
                    print(f"[Theme] Callback error: {e}")
            
            return True
        return False
    
    def register_callback(self, callback):
        """Register a callback for theme changes"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def unregister_callback(self, callback):
        """Unregister a theme change callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_available_themes(self):
        """Get list of all available theme names"""
        preset_names = [t.name for t in self.THEMES.values()]
        custom_names = [t.name for t in self.custom_themes.values()]
        return preset_names + custom_names
    
    def create_custom_theme(self, name, colors, fonts=None, effects=None):
        """Create and save a custom theme"""
        theme = Theme(name, colors, fonts, effects)
        self.custom_themes[name.lower()] = theme
        self.save_config()
        return theme
    
    def delete_custom_theme(self, name):
        """Delete a custom theme"""
        theme_key = name.lower()
        if theme_key in self.custom_themes:
            del self.custom_themes[theme_key]
            self.save_config()
            return True
        return False
    
    def export_theme(self, theme_name, filename):
        """Export theme to JSON file"""
        theme = self.get_theme(theme_name)
        if theme:
            try:
                with open(filename, 'w') as f:
                    json.dump(theme.to_dict(), f, indent=4)
                return True
            except Exception as e:
                print(f"[Theme] Export error: {e}")
        return False
    
    def import_theme(self, filename):
        """Import theme from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                theme = Theme.from_dict(data)
                self.custom_themes[theme.name.lower()] = theme
                self.save_config()
                return theme
        except Exception as e:
            print(f"[Theme] Import error: {e}")
            return None


# Global theme manager instance
_theme_manager = None

def get_theme_manager():
    """Get or create global theme manager"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
