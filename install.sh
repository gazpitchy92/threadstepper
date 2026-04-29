#!/bin/bash
source ./settings
current_dir=$(pwd)
clear

echo "This will install 7zip, stress-ng and download ungoogled-chromium executable. Continue? [Y/n]"
read -r response

if [[ "$response" =~ ^[Nn]$ ]]; then
    echo "Installation aborted."
    exit 0
fi

install_failed() {
    echo "There has been an error. Please manually install 7zip and stress-ng to use threadstepper."
    exit 1
}

if command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm stress-ng || install_failed
    sudo pacman -Sy --noconfirm p7zip || install_failed
elif command -v apt &>/dev/null; then
    sudo apt update && sudo apt install -y p7zip-full stress-ng || install_failed
elif command -v dnf &>/dev/null; then
    sudo dnf install -y p7zip stress-ng || install_failed
elif command -v zypper &>/dev/null; then
    sudo zypper install -y p7zip stress-ng || install_failed
else
    echo "Unsupported package manager"
    install_failed
fi

# Setup virtual environment and install requirements
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Dependencies have been installed"

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
