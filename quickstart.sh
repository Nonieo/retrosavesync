#!/bin/bash
# Quick start script for RetroSaveSync
# This script helps you get started quickly

echo "====================================="
echo "RetroSaveSync Quick Start"
echo "====================================="
echo ""

# Check if config.json exists
if [ -f "config.json" ]; then
    echo "✓ Configuration file found"
else
    echo "✗ Configuration file not found"
    echo ""
    echo "Creating config.json from template..."
    
    if [ -f "config.example.json" ]; then
        cp config.example.json config.json
        echo "✓ Created config.json"
        echo ""
        echo "Please edit config.json and update:"
        echo "  1. nas_path - Path to your NAS/network share"
        echo "  2. save_path values for each emulator"
        echo ""
        echo "Then run this script again."
        exit 0
    else
        echo "✗ config.example.json not found"
        exit 1
    fi
fi

echo ""
echo "What would you like to do?"
echo "1) Test configuration (dry run)"
echo "2) Sync all emulators"
echo "3) Sync PCSX2 only"
echo "4) Sync Dolphin only"
echo "5) Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Running dry run..."
        python3 retrosavesync.py --dry-run
        ;;
    2)
        echo ""
        echo "Syncing all emulators..."
        python3 retrosavesync.py
        ;;
    3)
        echo ""
        echo "Syncing PCSX2..."
        python3 retrosavesync.py -e pcsx2
        ;;
    4)
        echo ""
        echo "Syncing Dolphin..."
        python3 retrosavesync.py -e dolphin
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Done!"
