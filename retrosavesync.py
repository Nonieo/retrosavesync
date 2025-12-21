#!/usr/bin/env python3
"""
RetroSaveSync - Synchronize emulator saves between local storage and NAS

This tool syncs save files for various emulators (PCSX2, Dolphin) between
local directories and a NAS, keeping the most recent version.
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class SaveSync:
    """Handles synchronization of save files between local and NAS storage."""
    
    def __init__(self, config_path: str):
        """Initialize SaveSync with configuration file.
        
        Args:
            config_path: Path to JSON configuration file
        """
        self.config = self._load_config(config_path)
        self.nas_path = Path(self.config['nas_path']).expanduser()
        self.sync_stats = {
            'uploaded': 0,
            'downloaded': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def _load_config(self, config_path: str) -> Dict:
        """Load and validate configuration from JSON file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'nas_path' not in config:
            raise ValueError("Configuration must include 'nas_path'")
        if 'emulators' not in config:
            raise ValueError("Configuration must include 'emulators'")
            
        return config
    
    def _get_file_mtime(self, file_path: Path) -> float:
        """Get modification time of a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Modification time as timestamp, or 0 if file doesn't exist
        """
        try:
            return file_path.stat().st_mtime
        except FileNotFoundError:
            return 0.0
    
    def _sync_file(self, local_path: Path, nas_path: Path, direction: str = 'auto') -> bool:
        """Sync a single file between local and NAS.
        
        Args:
            local_path: Local file path
            nas_path: NAS file path
            direction: 'auto' (based on timestamp), 'upload', or 'download'
            
        Returns:
            True if sync was performed, False if skipped
        """
        local_exists = local_path.exists()
        nas_exists = nas_path.exists()
        
        # If neither exists, nothing to sync
        if not local_exists and not nas_exists:
            return False
        
        # Determine sync direction
        if direction == 'auto':
            if not nas_exists:
                direction = 'upload'
            elif not local_exists:
                direction = 'download'
            else:
                local_mtime = self._get_file_mtime(local_path)
                nas_mtime = self._get_file_mtime(nas_path)
                
                if local_mtime > nas_mtime:
                    direction = 'upload'
                elif nas_mtime > local_mtime:
                    direction = 'download'
                else:
                    # Files are identical in timestamp
                    self.sync_stats['skipped'] += 1
                    return False
        
        try:
            if direction == 'upload':
                # Ensure NAS directory exists
                nas_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(local_path, nas_path)
                print(f"  ↑ Uploaded: {local_path.name}")
                self.sync_stats['uploaded'] += 1
                return True
            elif direction == 'download':
                # Ensure local directory exists
                local_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(nas_path, local_path)
                print(f"  ↓ Downloaded: {local_path.name}")
                self.sync_stats['downloaded'] += 1
                return True
        except Exception as e:
            print(f"  ✗ Error syncing {local_path.name}: {e}")
            self.sync_stats['errors'] += 1
            return False
        
        return False
    
    def _sync_directory(self, local_dir: Path, nas_dir: Path, 
                       recursive: bool = True, extensions: List[str] = None) -> None:
        """Sync all files in a directory between local and NAS.
        
        Args:
            local_dir: Local directory path
            nas_dir: NAS directory path
            recursive: Whether to sync subdirectories recursively
            extensions: List of file extensions to sync (e.g., ['.ps2', '.gci'])
        """
        local_dir = local_dir.expanduser()
        
        # Collect all files from both locations
        local_files = set()
        nas_files = set()
        
        if local_dir.exists():
            if recursive:
                for file_path in local_dir.rglob('*'):
                    if file_path.is_file():
                        if extensions is None or file_path.suffix.lower() in extensions:
                            rel_path = file_path.relative_to(local_dir)
                            local_files.add(rel_path)
            else:
                for file_path in local_dir.glob('*'):
                    if file_path.is_file():
                        if extensions is None or file_path.suffix.lower() in extensions:
                            rel_path = file_path.relative_to(local_dir)
                            local_files.add(rel_path)
        
        if nas_dir.exists():
            if recursive:
                for file_path in nas_dir.rglob('*'):
                    if file_path.is_file():
                        if extensions is None or file_path.suffix.lower() in extensions:
                            rel_path = file_path.relative_to(nas_dir)
                            nas_files.add(rel_path)
            else:
                for file_path in nas_dir.glob('*'):
                    if file_path.is_file():
                        if extensions is None or file_path.suffix.lower() in extensions:
                            rel_path = file_path.relative_to(nas_dir)
                            nas_files.add(rel_path)
        
        # Sync all unique files
        all_files = local_files | nas_files
        for rel_path in sorted(all_files):
            local_file = local_dir / rel_path
            nas_file = nas_dir / rel_path
            self._sync_file(local_file, nas_file)
    
    def sync_pcsx2(self) -> None:
        """Sync PCSX2 (PS2) save files."""
        config = self.config['emulators'].get('pcsx2', {})
        
        if not config.get('enabled', False):
            print("PCSX2 sync is disabled")
            return
        
        local_path = Path(config['save_path']).expanduser()
        nas_path = self.nas_path / 'PCSX2'
        
        print(f"\nSyncing PCSX2 saves:")
        print(f"  Local: {local_path}")
        print(f"  NAS: {nas_path}")
        
        # Sync memory card files
        self._sync_directory(local_path, nas_path, recursive=True)
    
    def sync_dolphin(self) -> None:
        """Sync Dolphin (Wii/GameCube) save files."""
        config = self.config['emulators'].get('dolphin', {})
        
        if not config.get('enabled', False):
            print("Dolphin sync is disabled")
            return
        
        base_path = Path(config['save_path']).expanduser()
        nas_base = self.nas_path / 'Dolphin'
        saves_config = config.get('saves', {})
        
        print(f"\nSyncing Dolphin saves:")
        print(f"  Local: {base_path}")
        print(f"  NAS: {nas_base}")
        
        # Sync Wii saves
        if 'wii' in saves_config:
            wii_local = base_path / saves_config['wii']
            wii_nas = nas_base / 'Wii'
            print(f"\n  Wii saves:")
            self._sync_directory(wii_local, wii_nas, recursive=True)
        
        # Sync GameCube saves
        if 'gamecube' in saves_config:
            gc_local = base_path / saves_config['gamecube']
            gc_nas = nas_base / 'GC'
            print(f"\n  GameCube saves:")
            self._sync_directory(gc_local, gc_nas, recursive=True)
    
    def sync_all(self) -> None:
        """Sync all enabled emulators."""
        print("=" * 60)
        print("RetroSaveSync - Starting synchronization")
        print("=" * 60)
        
        # Ensure NAS path exists
        if not self.nas_path.exists():
            print(f"\nCreating NAS directory: {self.nas_path}")
            try:
                self.nas_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Error creating NAS directory: {e}")
                return
        
        # Sync each emulator
        emulators = self.config.get('emulators', {})
        
        if 'pcsx2' in emulators:
            self.sync_pcsx2()
        
        if 'dolphin' in emulators:
            self.sync_dolphin()
        
        # Print summary
        print("\n" + "=" * 60)
        print("Synchronization complete!")
        print(f"  Uploaded: {self.sync_stats['uploaded']}")
        print(f"  Downloaded: {self.sync_stats['downloaded']}")
        print(f"  Skipped: {self.sync_stats['skipped']}")
        print(f"  Errors: {self.sync_stats['errors']}")
        print("=" * 60)


def main():
    """Main entry point for RetroSaveSync."""
    parser = argparse.ArgumentParser(
        description='Synchronize emulator saves between local storage and NAS'
    )
    parser.add_argument(
        '-c', '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '-e', '--emulator',
        choices=['all', 'pcsx2', 'dolphin'],
        default='all',
        help='Emulator to sync (default: all)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be synced without actually syncing'
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"Error: Configuration file '{args.config}' not found")
        print(f"Please create a config.json file. See config.example.json for reference.")
        sys.exit(1)
    
    try:
        syncer = SaveSync(args.config)
        
        if args.emulator == 'all':
            syncer.sync_all()
        elif args.emulator == 'pcsx2':
            syncer.sync_pcsx2()
        elif args.emulator == 'dolphin':
            syncer.sync_dolphin()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
