# RetroSaveSync

A Python tool to synchronize emulator save files between local storage and a NAS (Network Attached Storage). The tool intelligently syncs files based on modification timestamps, ensuring you always have the most recent saves available.

## Features

- **Bidirectional Sync**: Automatically uploads local saves to NAS and downloads NAS saves to local storage based on which is more recent
- **PCSX2 Support**: Sync PS2 memory card files
- **Dolphin Support**: Sync Wii and GameCube save files
- **Configurable**: Easy JSON configuration for paths and emulator settings
- **Safe**: Preserves file timestamps and only syncs when necessary

## Requirements

- Python 3.6 or higher
- Access to a NAS or network share

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Nonieo/retrosavesync.git
cd retrosavesync
```

2. Make the script executable (optional):
```bash
chmod +x retrosavesync.py
```

## Configuration

1. Copy the example configuration file:
```bash
cp config.example.json config.json
```

2. Edit `config.json` with your paths:

```json
{
  "nas_path": "/path/to/nas/retro_saves",
  "emulators": {
    "pcsx2": {
      "enabled": true,
      "save_path": "~/.config/PCSX2/memcards",
      "description": "PCSX2 (PS2) save files"
    },
    "dolphin": {
      "enabled": true,
      "save_path": "~/.local/share/dolphin-emu",
      "saves": {
        "wii": "Wii",
        "gamecube": "GC"
      },
      "description": "Dolphin (Wii/GameCube) save files"
    }
  }
}
```

### Configuration Options

- **nas_path**: Path to your NAS or network share where saves will be stored
- **emulators**: Dictionary of emulator configurations
  - **enabled**: Set to `true` to enable syncing for this emulator
  - **save_path**: Path to the emulator's save directory
  - **saves** (Dolphin only): Subdirectories for different console types

### Common Paths

**PCSX2:**
- Linux: `~/.config/PCSX2/memcards`
- Windows: `%USERPROFILE%\Documents\PCSX2\memcards`
- macOS: `~/Library/Application Support/PCSX2/memcards`

**Dolphin:**
- Linux: `~/.local/share/dolphin-emu`
- Windows: `%USERPROFILE%\Documents\Dolphin Emulator`
- macOS: `~/Library/Application Support/Dolphin`

## Usage

### Sync All Emulators

```bash
python3 retrosavesync.py
```

### Sync Specific Emulator

```bash
# Sync only PCSX2
python3 retrosavesync.py -e pcsx2

# Sync only Dolphin
python3 retrosavesync.py -e dolphin
```

### Use Custom Config File

```bash
python3 retrosavesync.py -c /path/to/config.json
```

### Command Line Options

- `-c, --config`: Path to configuration file (default: config.json)
- `-e, --emulator`: Emulator to sync - choices: all, pcsx2, dolphin (default: all)
- `--dry-run`: Show what would be synced without actually syncing (planned feature)

## How It Works

1. **Compares Timestamps**: For each save file, the tool compares modification times between local and NAS versions
2. **Syncs Newer Files**: 
   - If the local file is newer, it uploads to NAS
   - If the NAS file is newer, it downloads to local
   - If timestamps match, the file is skipped
3. **Creates Missing Directories**: Automatically creates necessary directories on both local and NAS
4. **Preserves Metadata**: Uses `shutil.copy2()` to preserve file timestamps and permissions

## Example Output

```
============================================================
RetroSaveSync - Starting synchronization
============================================================

Syncing PCSX2 saves:
  Local: /home/user/.config/PCSX2/memcards
  NAS: /mnt/nas/retro_saves/PCSX2
  ↑ Uploaded: Mcd001.ps2
  ↓ Downloaded: Mcd002.ps2

Syncing Dolphin saves:
  Local: /home/user/.local/share/dolphin-emu
  NAS: /mnt/nas/retro_saves/Dolphin

  Wii saves:
  ↑ Uploaded: MarioKart.bin

  GameCube saves:
  ↓ Downloaded: SuperSmashBros.gci

============================================================
Synchronization complete!
  Uploaded: 2
  Downloaded: 2
  Skipped: 5
  Errors: 0
============================================================
```

## Automation

You can automate syncing using cron (Linux/macOS) or Task Scheduler (Windows):

### Linux/macOS Cron Example

```bash
# Edit crontab
crontab -e

# Add this line to sync every hour
0 * * * * cd /path/to/retrosavesync && python3 retrosavesync.py
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create a new task
3. Set trigger (e.g., on startup, hourly)
4. Set action to run: `python C:\path\to\retrosavesync.py`

## Safety Notes

- The tool uses file modification times to determine which version is newer
- Original files are overwritten when a newer version is found
- Consider backing up your saves before first use
- Test with a few save files first to ensure paths are configured correctly

## Troubleshooting

**"Configuration file not found"**
- Make sure you've created `config.json` from `config.example.json`

**"Permission denied"**
- Ensure you have read/write access to both local save directories and NAS

**Files not syncing**
- Check that paths in config.json are correct
- Verify emulators are enabled in config
- Ensure NAS is mounted and accessible

## License

MIT License - Feel free to modify and distribute

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
