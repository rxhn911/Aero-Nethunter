#!/usr/bin/env python3
"""
Performance Manager Module for Aero Nethunter
Handles caching, connection pooling, and resource monitoring
"""

import json
import os
import time
import psutil
from threading import Lock
from collections import OrderedDict
from datetime import datetime, timedelta


class LRUCache:
    """Thread-safe LRU Cache implementation"""
    def __init__(self, max_size=1000):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.lock = Lock()
        self.hits = 0
        self.misses = 0
        
    def get(self, key):
        """Get value from cache"""
        with self.lock:
            if key in self.cache:
                self.hits += 1
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            else:
                self.misses += 1
                return None
    
    def put(self, key, value):
        """Put value into cache"""
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache.move_to_end(key)
            else:
                # Add new
                if len(self.cache) >= self.max_size:
                    # Remove oldest
                    self.cache.popitem(last=False)
            self.cache[key] = value
    
    def get_stats(self):
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": total,
            "hit_rate": hit_rate,
            "size": len(self.cache)
        }
    
    def clear(self):
        """Clear cache"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0


class MACVendorCache:
    """MAC Vendor lookup caching system"""
    def __init__(self, cache_file="mac_vendor_cache.json", max_size=1000):
        self.cache = LRUCache(max_size)
        self.cache_file = cache_file
        self.last_save = time.time()
        self.save_interval = 300  # Save every 5 minutes
        self.load_from_disk()
    
    def lookup(self, mac, lookup_func):
        """
        Lookup MAC vendor with caching
        Args:
            mac: MAC address
            lookup_func: Function to call if not in cache
        """
        # Normalize MAC address
        mac_normalized = mac.upper().replace(":", "").replace("-", "")
        
        # Check cache first
        vendor = self.cache.get(mac_normalized)
        if vendor is not None:
            return vendor
        
        # Cache miss - perform actual lookup
        try:
            vendor = lookup_func(mac)
            self.cache.put(mac_normalized, vendor)
            
            # Auto-save periodically
            if time.time() - self.last_save > self.save_interval:
                self.save_to_disk()
            
            return vendor
        except Exception as e:
            # Cache the error as "Unknown" to avoid repeated failures
            self.cache.put(mac_normalized, "Unknown")
            return "Unknown"
    
    def load_from_disk(self):
        """Load cache from disk"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    for mac, vendor in data.items():
                        self.cache.put(mac, vendor)
                print(f"[Cache] Loaded {len(data)} MAC vendors from disk")
            except Exception as e:
                print(f"[Cache] Error loading: {e}")
    
    def save_to_disk(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(dict(self.cache.cache), f)
            self.last_save = time.time()
            print(f"[Cache] Saved {len(self.cache.cache)} entries to disk")
        except Exception as e:
            print(f"[Cache] Error saving: {e}")
    
    def get_stats(self):
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)


class ConnectionPool:
    """Simple connection pooling for socket operations"""
    def __init__(self, max_connections=50):
        self.max_connections = max_connections
        self.active_connections = 0
        self.total_created = 0
        self.total_reused = 0
        self.lock = Lock()
    
    def acquire(self):
        """Acquire a connection slot"""
        with self.lock:
            if self.active_connections < self.max_connections:
                self.active_connections += 1
                self.total_created += 1
                return True
            return False
    
    def release(self):
        """Release a connection slot"""
        with self.lock:
            if self.active_connections > 0:
                self.active_connections -= 1
    
    def get_stats(self):
        """Get connection pool statistics"""
        return {
            "active": self.active_connections,
            "max": self.max_connections,
            "created": self.total_created,
            "reused": self.total_reused
        }


class ResourceMonitor:
    """Monitor system resource usage"""
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = time.time()
        self.scan_count = 0
        self.device_count = 0
        
    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        try:
            return self.process.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        try:
            mem_info = self.process.memory_info()
            return mem_info.rss / (1024 * 1024)  # Convert to MB
        except:
            return 0.0
    
    def get_memory_percent(self):
        """Get memory usage as percentage of total system memory"""
        try:
            return self.process.memory_percent()
        except:
            return 0.0
    
    def get_network_io(self):
        """Get network I/O statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except:
            return {"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0}
    
    def get_uptime(self):
        """Get application uptime"""
        return time.time() - self.start_time
    
    def get_scan_rate(self):
        """Get scans per second"""
        uptime = self.get_uptime()
        if uptime > 0:
            return self.scan_count / uptime
        return 0.0
    
    def increment_scan(self):
        """Increment scan counter"""
        self.scan_count += 1
    
    def update_device_count(self, count):
        """Update device count"""
        self.device_count = count
    
    def get_stats(self):
        """Get all resource statistics"""
        return {
            "cpu_percent": round(self.get_cpu_usage(), 2),
            "memory_mb": round(self.get_memory_usage(), 2),
            "memory_percent": round(self.get_memory_percent(), 2),
            "uptime_seconds": round(self.get_uptime(), 2),
            "scan_count": self.scan_count,
            "scan_rate": round(self.get_scan_rate(), 2),
            "device_count": self.device_count,
            "network_io": self.get_network_io()
        }


class PerformanceManager:
    """Central performance management class"""
    def __init__(self, config=None):
        self.config = config or self.default_config()
        
        # Initialize components
        self.mac_cache = MACVendorCache(
            max_size=self.config.get("cache_size", 1000)
        )
        self.connection_pool = ConnectionPool(
            max_connections=self.config.get("max_connections", 50)
        )
        self.resource_monitor = ResourceMonitor()
        
        # Performance metrics
        self.metrics = {
            "last_scan_duration": 0,
            "avg_scan_duration": 0,
            "total_scans": 0
        }
    
    @staticmethod
    def default_config():
        """Default configuration"""
        return {
            "cache_size": 1000,
            "max_connections": 50,
            "scan_interval": 3,
            "thread_pool_size": 10,
            "port_scan_timeout": 1.0
        }
    
    def start_scan_timer(self):
        """Start timing a scan operation"""
        return time.time()
    
    def end_scan_timer(self, start_time):
        """End timing a scan operation"""
        duration = time.time() - start_time
        self.metrics["last_scan_duration"] = duration
        self.metrics["total_scans"] += 1
        
        # Update average
        total = self.metrics["total_scans"]
        avg = self.metrics["avg_scan_duration"]
        self.metrics["avg_scan_duration"] = (avg * (total - 1) + duration) / total
        
        self.resource_monitor.increment_scan()
    
    def get_all_stats(self):
        """Get all performance statistics"""
        return {
            "cache": self.mac_cache.get_stats(),
            "connection_pool": self.connection_pool.get_stats(),
            "resources": self.resource_monitor.get_stats(),
            "metrics": self.metrics,
            "config": self.config
        }
    
    def cleanup(self):
        """Cleanup and save state"""
        self.mac_cache.save_to_disk()


# Global instance
_perf_manager = None

def get_performance_manager():
    """Get or create global performance manager instance"""
    global _perf_manager
    if _perf_manager is None:
        _perf_manager = PerformanceManager()
    return _perf_manager
