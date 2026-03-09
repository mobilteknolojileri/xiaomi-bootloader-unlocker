# Xiaomi Bootloader Unlocker

[![GitHub Stars](https://img.shields.io/github/stars/mobilteknolojileri/xiaomi-bootloader-unlocker?style=flat-square)](https://github.com/mobilteknolojileri/xiaomi-bootloader-unlocker/stargazers)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

Xiaomi limits bootloader unlock applications to a fixed daily quota (commonly reported as around 2,000). The quota resets at midnight Beijing time (UTC+8). This tool fires **30 parallel requests** at that reset moment to improve your chances of getting a slot.

Log in, set your delay, and walk away. The tool handles the rest.

---

## What does it do?

- Logs into your Xiaomi account
- Checks if your account is eligible
- Syncs Beijing time from NTP servers (doesn't rely on your system clock)
- At the right moment, sends **30 threaded requests** simultaneously
- Saves everything to `logs/` for debugging

## Setup

```bash
git clone https://github.com/mobilteknolojileri/xiaomi-bootloader-unlocker.git
cd xiaomi-bootloader-unlocker
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

It will ask for:
1. Xiaomi account (email or phone)
2. Password
3. Delay in ms — press Enter for default (100ms)

You can also pass the delay directly:

```bash
python main.py --delay 100
```

### When to run

Figure out when midnight Beijing time is in your timezone, then start the script 2–5 minutes early:

| Region | Start at | Beijing midnight |
|---|---|---|
| Turkey (UTC+3) | 18:55 | 19:00 |
| Germany (UTC+1) | 16:55 | 17:00 |
| UK (UTC+0) | 15:55 | 16:00 |
| India (UTC+5:30) | 21:25 | 21:30 |
| US East (UTC-5) | 10:55 | 11:00 |

### What delay should I use?

These are rough starting points based on community experience. Check your latency first:

```bash
ping sgp-api.buy.mi.com
```

| Ping | Suggested delay |
|---|---|
| Under 100ms | `100` (optimized default) |
| 100–300ms | `300–800` |
| Over 300ms | `1000+` |

## How it works

```
Login → Status check → NTP sync → Wait → BURST (30 requests in ~450ms) → Done
```

1. Authenticates with Xiaomi's API and grabs a session token
2. Verifies your account can actually apply
3. Pulls accurate Beijing time from 7 NTP servers
4. Waits until the configured time before midnight
5. Spawns 30 threads, each sending `POST /apply/bl-auth` (15ms apart)
6. Prints results to terminal and writes them to a log file

## After approval

Once you get approved (process may vary by device/region):

1. Wait for the cooling period (typically **72 hours**, can vary)
2. Download **Mi Unlock Tool** on PC
3. Boot your phone into fastboot (power + volume down)
4. Connect via USB and unlock through Mi Unlock Tool

## Project structure

```
├── main.py            # Entry point, CLI args
├── auth.py            # Xiaomi account login
├── bootloader.py      # BURST mode, 10 threaded requests
├── config.py          # Delay settings
├── device.py          # Device ID generation
├── http_session.py    # HTTP connection pooling
├── status_checker.py  # Account eligibility check
├── time_sync.py       # NTP time synchronization
├── logger.py          # Terminal + file logging
└── logs/              # Auto-generated session logs
```

## FAQ

**Does it work on mobile?**
Yes, with Pydroid 3 on Android. But PC gives better timing accuracy — use that if you can.

**Will I get banned?**
30 requests in under 0.5 seconds is aggressive but focused on a single moment in the day. To minimize risk, the script only runs the burst once. No bans have been reported for this level of activity during the global reset window, but proceed with caution.

**First attempt failed, what now?**
Try again next day. Bump the delay up a bit (try 1500ms). The quota fills fast.

**Does it work with 2FA enabled?**
No. You need to temporarily disable 2FA for the login to work.

## Disclaimer

This tool is for educational purposes only. Use at your own risk. The developer is not responsible for any issues that may arise from using this tool.

## License

[MIT](LICENSE)

## Contributing

Pull requests and issues are welcome.

---

If this helped you, drop a ⭐ so others can find it too.
