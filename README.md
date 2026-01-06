# Xiaomi Bootloader Unlocker

![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)
[![GitHub Stars](https://img.shields.io/github/stars/mobilteknolojileri/xiaomi-bootloader-unlocker?style=for-the-badge&logo=github)](https://github.com/mobilteknolojileri/xiaomi-bootloader-unlocker/stargazers)

> 🚀 Automated Xiaomi bootloader unlock application tool with NTP time sync and millisecond precision.

## ⚡ Features

- 🔐 **Xiaomi Account Authentication** - Secure login with your Xiaomi credentials
- ⏱️ **NTP Time Synchronization** - Accurate Beijing time sync for precise application timing
- 🎯 **Millisecond Precision** - Submit unlock applications at the exact right moment
- 🔄 **Automatic Retry** - Handles network errors and retries automatically
- 📊 **Status Checking** - Monitors your unlock application status in real-time

## 📋 Requirements

- Python 3.7+
- Xiaomi account with bootloader unlock eligibility

## 🚀 Installation

```bash
git clone https://github.com/mobilteknolojileri/xiaomi-bootloader-unlocker.git
cd xiaomi-bootloader-unlocker
pip install -r requirements.txt
```

## 💻 Usage

### Interactive Mode

```bash
python main.py
```

### CLI Mode (Advanced)

```bash
# Use custom delay
python main.py --delay 888
python main.py -d 500

# Show help
python main.py --help
```

### Steps

1. Enter your Xiaomi account credentials (email/phone and password)
2. Set the delay time in milliseconds (default: 888 ms) or press Enter for default
3. The tool will sync with Beijing time and submit your application at the optimal moment

## ⚙️ How It Works

The tool synchronizes with NTP servers to get accurate Beijing time (UTC+8), then submits your bootloader unlock application just before midnight. This timing strategy helps maximize the chances of a successful application.

### Delay Configuration

- **Default delay**: 888 ms before midnight
- The application is sent at `23:59:59.XXX` where XXX = 1000 - delay
- Example: 200 ms delay = application sent at 23:59:59.800

## ⚠️ Disclaimer

This tool is for educational purposes only. Use at your own risk. The developers are not responsible for any issues that may arise from using this tool.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⭐ Show Your Support

If this project helped you, please give it a star!
