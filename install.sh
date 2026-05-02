#!/bin/bash
source ./settings
current_dir=$(pwd)
clear

echo "This will download ungoogled-chromium executable. Continue? [Y/n]"
read -r response

if [[ "$response" =~ ^[Nn]$ ]]; then
    echo "Installation aborted."
    exit 0
fi

APPIMAGE_URL="$chromium_domain/$chromium_version/$chromium_appimage"
APPIMAGE_PATH="$current_dir/tests/browser/$chromium_appimage"

shopt -s globstar
rm -rf $current_dir/tests/browser/tmp 2>/dev/null || true
rm -rf $current_dir/tests/browser/tmpfile: 2>/dev/null || true
rm -rf $current_dir/tests/browser/**/*.AppImage 2>/dev/null || true
mkdir -p $current_dir/tests/browser/tmp

if [ ! -f "$APPIMAGE_PATH" ]; then
    echo "Downloading ungoogled-chromium AppImage..."
    wget -O "$APPIMAGE_PATH" "$APPIMAGE_URL" || { echo "Download failed"; exit 1; }
    chmod +x "$APPIMAGE_PATH"
else
    echo "AppImage already exists at $APPIMAGE_PATH"
fi

chmod +x ./threadstepper

clear
echo "You can now use Thread Stepper!"
echo "Please close this window..."
