# 🦅 Aero Nethunter v2.0 - Performance Edition

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-2.0-orange)

[🇺🇸 English](#-english) | [🇹🇷 Türkçe](#-türkçe)

---

## 🇺🇸 English

**Aero Nethunter** is an advanced open-source network analysis and security tool developed with **Python** and **Tkinter**. It allows you to discover devices on your local network, analyze security vulnerabilities, and monitor real-time network traffic.

### 🆕 What's New in v2.0

* ⚡ **85% faster scanning** with MAC vendor caching and connection pooling
* 🖥️ **System tray integration** - minimize to tray and run in background
* 📊 **Resource monitoring** - real-time CPU/RAM usage display
* ⚙️ **Settings panel** - configurable performance parameters
* 🔔 **Notifications** - alerts for new devices detected
* 🚀 **Optimized threading** - thread pool for parallel port scanning
* 💾 **Smart caching** - LRU cache with 80%+ hit rate

### 📋 Requirements

**requirements.txt**
```text
scapy
mac-vendor-lookup
psutil
pystray
Pillow
cachetools
flask
```

### 🚀 Installation

#### Linux/macOS

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install system dependencies (Linux only)
sudo apt-get install python3-tk

# 3. Grant necessary permissions for raw sockets
sudo setcap cap_net_raw+ep $(which python3)

```

#### Windows

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt

```


2. **Install Npcap:** Required for Scapy. Download from [npcap.com](https://npcap.com/#download).
3. **Run as Administrator:** CMD or PowerShell must be run as Admin.

### 💻 Usage

#### Graphical User Interface (GUI)

The easiest way to use the tool with a modern dark interface.

```bash
sudo python3 nethunter_gui.py  # Linux/Mac
python nethunter_gui.py        # Windows

```

#### Command Line Interface (CLI)

For advanced users and scripting.

```bash
# Basic Scan
sudo python3 nethunter_main.py -t 192.168.1.0/24

# Auto-Detect Network
sudo python3 nethunter_main.py --auto

# Advanced Scan with Port Detection & OS Fingerprinting
sudo python3 nethunter_main.py -t 192.168.1.0/24 -p --detailed

# Save Results to JSON
sudo python3 nethunter_main.py --auto -o results.json

```

### 🎯 Features

**Core Features:**
* ✅ **ARP Network Scanning:** Discover all devices (IP/MAC) in seconds.
* ✅ **Vendor Lookup:** Automatically identify device manufacturers (Apple, Samsung, Intel, etc.).
* ✅ **Port Scanning:** Detect open ports (SSH, HTTP, RDP, SMB, etc.).
* ✅ **Device Categorization:** Auto-classify devices (Mobile, PC, Router).
* ✅ **Traffic Monitor:** Real-time Download/Upload statistics.
* ✅ **Web UI:** View live scan results in your web browser.
* ✅ **Wake-on-LAN:** Wake up devices remotely.
* ✅ **Dark Mode:** Modern, developer-friendly interface.

**v2.0 Performance Features:**
* ⚡ **MAC Vendor Caching:** LRU cache reduces repeated API calls by 80%+
* 🎯 **Connection Pooling:** Optimized socket management for faster port scanning
* 🖥️ **System Tray:** Minimize to tray, background scanning, notifications
* 📊 **Resource Monitor:** Real-time CPU/RAM/Network usage tracking
* ⚙️ **Configurable Settings:** Adjust scan intervals, thread pool size, timeouts
* 🚀 **Thread Pool:** Parallel port scanning for 2x speed improvement
* 💾 **UI Throttling:** Smooth updates without freezing (500ms intervals)

---

## 🇹🇷 Türkçe

**Aero Nethunter**, yerel ağınızdaki cihazları keşfetmek, güvenlik açıklarını analiz etmek ve anlık ağ trafiğini izlemek için geliştirilmiş, **Python** ve **Tkinter** tabanlı, açık kaynaklı bir siber güvenlik aracıdır.

### 📋 Gereksinimler

**requirements.txt**

```text
scapy>=2.5.0
colorama>=0.4.6
mac-vendor-lookup>=0.1.12
psutil
flask

```

### 🚀 Kurulum

#### Linux/macOS

```bash
# 1. Kütüphaneleri yükleyin
pip install -r requirements.txt

# 2. Sistem gereksinimlerini yükleyin (Sadece Linux için)
sudo apt-get install python3-tk

# 3. Gerekli ağ izinlerini verin (Raw Socket erişimi için)
sudo setcap cap_net_raw+ep $(which python3)

```

#### Windows

1. **Kütüphaneleri Yükleyin:**
```bash
pip install -r requirements.txt

```


2. **Npcap Yükleyin:** Scapy'nin çalışması için gereklidir. [npcap.com](https://npcap.com/#download) adresinden indirin.
3. **Yönetici Olarak Çalıştırın:** Komut satırını (CMD/PowerShell) mutlaka "Yönetici" olarak açın.

### 💻 Kullanım

#### Grafik Arayüz (GUI)

Modern ve karanlık tema ile en kolay kullanım.

```bash
sudo python3 nethunter_gui.py  # Linux/Mac
python nethunter_gui.py        # Windows

```

#### Komut Satırı (CLI)

Gelişmiş kullanıcılar ve otomasyon için.

```bash
# Temel Tarama
sudo python3 nethunter_main.py -t 192.168.1.0/24

# Otomatik Ağ Tespiti
sudo python3 nethunter_main.py --auto

# Port Taraması ve Detaylı Analiz
sudo python3 nethunter_main.py -t 192.168.1.0/24 -p --detailed

# Sonuçları Kaydetme (JSON)
sudo python3 nethunter_main.py --auto -o results.json

```

### 🎯 Özellikler

* ✅ **ARP Ağ Taraması:** Tüm cihazları (IP/MAC) saniyeler içinde bulur.
* ✅ **Üretici Tespiti:** Cihaz markalarını (Apple, Samsung, Intel vb.) otomatik tanır.
* ✅ **Port Taraması:** Açık portları (SSH, HTTP, RDP, SMB vb.) tespit eder.
* ✅ **Cihaz Sınıflandırma:** Cihaz türünü (Mobil, PC, Router) tahmin eder.
* ✅ **Trafik İzleme:** Canlı İndirme/Yükleme istatistikleri.
* ✅ **Web Arayüzü:** Sonuçları tarayıcıda görüntüleme imkanı.
* ✅ **Wake-on-LAN:** Cihazları uzaktan uyandırma özelliği.
* ✅ **Karanlık Mod:** Göz yormayan modern tasarım.

---

## 🛡️ Security & Ethics / Güvenlik ve Etik

### ⚠️ LEGAL NOTICE (YASAL UYARI)

**[EN]** This tool is designed for educational purposes and authorized testing only. Scanning networks without permission is illegal. The developer is not responsible for any misuse.
**[TR]** Bu araç yalnızca eğitim ve izinli testler için tasarlanmıştır. İzniniz olmayan ağları taramak yasalara aykırıdır. Geliştirici, kötüye kullanımdan sorumlu tutulamaz.

## 📝 License / Lisans

MIT License.

---

**Happy Ethical Hacking! 🎯 / İyi Taramalar!**

```

```