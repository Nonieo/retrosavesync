# RetroSaveSync - Usage Examples

This document provides practical examples for common use cases.

## Basic Usage Examples

### First Time Setup

```bash
# 1. Clone and enter the repository
git clone https://github.com/Nonieo/retrosavesync.git
cd retrosavesync

# 2. Create your configuration
cp config.example.json config.json

# 3. Edit config.json with your paths
# Update nas_path to point to your NAS
# Update save_path for each emulator

# 4. Test your configuration
python3 retrosavesync.py --dry-run

# 5. Perform actual sync
python3 retrosavesync.py
```

### Daily Sync Workflow

```bash
# Sync all emulators before gaming session
python3 retrosavesync.py

# Play your games...

# Sync again after gaming to upload new saves
python3 retrosavesync.py
```

### Platform-Specific Paths

#### Linux Example
```json
{
  "nas_path": "/mnt/nas/retro_saves",
  "backup": {
    "enabled": true,
    "monthly_backups": true,
    "backup_path": "backups"
  },
  "emulators": {
    "pcsx2": {
      "enabled": true,
      "save_path": "~/.config/PCSX2/memcards"
    },
    "dolphin": {
      "enabled": true,
      "save_path": "~/.local/share/dolphin-emu",
      "saves": {
        "wii": "Wii",
        "gamecube": "GC"
      }
    }
  }
}
```

#### Windows Example
```json
{
  "nas_path": "Z:\\retro_saves",
  "backup": {
    "enabled": true,
    "monthly_backups": true,
    "backup_path": "backups"
  },
  "emulators": {
    "pcsx2": {
      "enabled": true,
      "save_path": "C:\\Users\\YourName\\Documents\\PCSX2\\memcards"
    },
    "dolphin": {
      "enabled": true,
      "save_path": "C:\\Users\\YourName\\Documents\\Dolphin Emulator",
      "saves": {
        "wii": "Wii",
        "gamecube": "GC"
      }
    }
  }
}
```

#### macOS Example
```json
{
  "nas_path": "/Volumes/NAS/retro_saves",
  "backup": {
    "enabled": true,
    "monthly_backups": true,
    "backup_path": "backups"
  },
  "emulators": {
    "pcsx2": {
      "enabled": true,
      "save_path": "~/Library/Application Support/PCSX2/memcards"
    },
    "dolphin": {
      "enabled": true,
      "save_path": "~/Library/Application Support/Dolphin",
      "saves": {
        "wii": "Wii",
        "gamecube": "GC"
      }
    }
  }
}
```

## Advanced Examples

### Monthly Backups

Enable automatic monthly backups to preserve save file history:

```json
{
  "nas_path": "/mnt/nas/retro_saves",
  "backup": {
    "enabled": true,
    "monthly_backups": true,
    "backup_path": "backups"
  },
  "emulators": {
    "pcsx2": {
      "enabled": true,
      "save_path": "~/.config/PCSX2/memcards"
    }
  }
}
```

When enabled, backups are automatically created before overwriting NAS files:

```bash
# Normal sync with backups enabled
python3 retrosavesync.py

# Output shows backup creation:
# 💾 Backed up: Mcd001.ps2 -> backups/2025-12/
# ↑ Uploaded: Mcd001.ps2
```

### Create Manual Backups

Create backups of all NAS saves without syncing:

```bash
# Create monthly backups
python3 retrosavesync.py --backup-only

# Test backup creation first
python3 retrosavesync.py --backup-only --dry-run
```

This is useful for:
- Creating a monthly snapshot before major gaming sessions
- Backing up saves before system updates
- Preserving saves before configuration changes

### Understanding Backup Structure

Backups are organized by year-month and preserve the full directory structure:

```
/mnt/nas/retro_saves/
├── PCSX2/                    # Current saves
│   └── Mcd001.ps2
├── Dolphin/                  # Current saves
│   ├── Wii/
│   │   └── MarioKart.bin
│   └── GC/
│       └── game.gci
└── backups/                  # Historical backups
    ├── 2025-11/              # November 2025 backups
    │   ├── PCSX2/
    │   │   └── Mcd001.ps2
    │   └── Dolphin/
    │       └── Wii/
    │           └── MarioKart.bin
    └── 2025-12/              # December 2025 backups
        ├── PCSX2/
        │   └── Mcd001.ps2
        └── Dolphin/
            ├── Wii/
            │   └── MarioKart.bin
            └── GC/
                └── game.gci
```

**Key Points:**
- Only one backup per file per month
- Backups are created only when a file would be overwritten
- Old backups are never automatically deleted
- You can manually clean up old backups as needed

### Sync Only PCSX2

Useful when you only play PS2 games:

```bash
python3 retrosavesync.py -e pcsx2
```

### Sync Only Dolphin

Useful when you only play Wii/GameCube games:

```bash
python3 retrosavesync.py -e dolphin
```

### Test Before Syncing

Always a good practice before syncing for the first time:

```bash
# See what would be synced
python3 retrosavesync.py --dry-run

# If it looks good, do the actual sync
python3 retrosavesync.py
```

### Disable an Emulator

Edit your config.json and set `enabled: false`:

```json
{
  "nas_path": "/mnt/nas/retro_saves",
  "emulators": {
    "pcsx2": {
      "enabled": false,
      "save_path": "~/.config/PCSX2/memcards"
    },
    "dolphin": {
      "enabled": true,
      "save_path": "~/.local/share/dolphin-emu",
      "saves": {
        "wii": "Wii",
        "gamecube": "GC"
      }
    }
  }
}
```

## Automation Examples

### Linux/macOS Cron Job

Sync every hour:

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths as needed)
0 * * * * cd /home/user/retrosavesync && /usr/bin/python3 retrosavesync.py >> /tmp/retrosavesync.log 2>&1
```

### Linux Systemd Timer

Create `/etc/systemd/user/retrosavesync.service`:

```ini
[Unit]
Description=RetroSaveSync Service

[Service]
Type=oneshot
WorkingDirectory=/home/user/retrosavesync
ExecStart=/usr/bin/python3 /home/user/retrosavesync/retrosavesync.py

[Install]
WantedBy=default.target
```

Create `/etc/systemd/user/retrosavesync.timer`:

```ini
[Unit]
Description=RetroSaveSync Timer

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
systemctl --user enable retrosavesync.timer
systemctl --user start retrosavesync.timer
```

### Windows Batch Script

Create `sync_saves.bat`:

```batch
@echo off
cd C:\Users\YourName\retrosavesync
python retrosavesync.py
pause
```

Add to Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Choose trigger (e.g., "Daily")
4. Action: "Start a program"
5. Program: `C:\Users\YourName\retrosavesync\sync_saves.bat`

## Troubleshooting Examples

### Check What Would Be Synced

```bash
python3 retrosavesync.py --dry-run
```

### Sync with Detailed Output

The script already provides detailed output showing each file operation.

### Verify Configuration

```bash
# Check if config file is valid JSON
python3 -m json.tool config.json

# Should output formatted JSON if valid
```

### Test Network Access

```bash
# Test if NAS is accessible
ls -la /path/to/nas

# On Windows
dir Z:\
```

## Multi-Machine Setup

### Scenario: Gaming PC and Gaming Laptop

Both machines share saves via NAS.

**Setup on both machines:**

1. Install RetroSaveSync
2. Use identical config.json on both machines
3. Run sync before and after gaming sessions

**Workflow:**

Gaming PC:
```bash
# Before playing
python3 retrosavesync.py  # Downloads latest saves from NAS

# After playing  
python3 retrosavesync.py  # Uploads new saves to NAS
```

Laptop:
```bash
# Before playing (downloads saves you created on PC)
python3 retrosavesync.py

# After playing (uploads new saves)
python3 retrosavesync.py
```

## Tips

1. **Always run sync before gaming** to get the latest saves
2. **Always run sync after gaming** to upload your progress
3. **Use --dry-run** when testing configuration changes
4. **Check the output** to see what files were synced
5. **Automate it** with cron/Task Scheduler for convenience
6. **Back up your NAS** - it's your central save repository
