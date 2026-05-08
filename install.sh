#!/bin/bash
source ./settings
current_dir=$(pwd)
clear

echo "This will install all optional dependencies. Continue? [Y/n]"
read -r response
if [[ "$response" =~ ^[Nn]$ ]]; then
    echo "Installation aborted."
    exit 0
fi

installElectron(){
    echo "$(tput setaf 4)Checking for existing Electron installation...$(tput sgr0)"
    existing=$(compgen -c | grep '^electron[0-9]' | sort -V | tail -1)
    if [ -n "$existing" ]; then
        echo "$(tput setaf 2)Electron already installed: $existing$(tput sgr0)"
        return 0
    fi

    if command -v pacman &>/dev/null; then
        echo "$(tput setaf 4)Detected pacman — installing electron41...$(tput sgr0)"
        if ! sudo pacman -S electron41 --noconfirm; then
            echo "$(tput setaf 1)!!!!! pacman install failed !!!!!$(tput sgr0)"
            return 1
        fi

    elif command -v apt-get &>/dev/null; then
        echo "$(tput setaf 4)Detected apt — installing Electron via npm...$(tput sgr0)"
        if ! command -v npm &>/dev/null; then
            echo "$(tput setaf 4)npm not found, installing nodejs/npm first...$(tput sgr0)"
            if ! sudo apt-get install -y nodejs npm; then
                echo "$(tput setaf 1)!!!!! Failed to install nodejs/npm !!!!!$(tput sgr0)"
                return 1
            fi
        fi
        if ! sudo npm install -g electron; then
            echo "$(tput setaf 1)!!!!! npm install failed !!!!!$(tput sgr0)"
            return 1
        fi

    elif command -v dnf &>/dev/null; then
        echo "$(tput setaf 4)Detected dnf — installing Electron via npm...$(tput sgr0)"
        if ! command -v npm &>/dev/null; then
            echo "$(tput setaf 4)npm not found, installing nodejs/npm first...$(tput sgr0)"
            if ! sudo dnf install -y nodejs npm; then
                echo "$(tput setaf 1)!!!!! Failed to install nodejs/npm !!!!!$(tput sgr0)"
                return 1
            fi
        fi
        if ! sudo npm install -g electron; then
            echo "$(tput setaf 1)!!!!! npm install failed !!!!!$(tput sgr0)"
            return 1
        fi

    else
        echo "$(tput setaf 1)!!!!! No supported package manager found !!!!!$(tput sgr0)"
        echo "$(tput setaf 1)!!!!! Please install Electron manually !!!!!$(tput sgr0)"
        return 1
    fi

    echo ""
    echo "$(tput setaf 4)Verifying installation...$(tput sgr0)"
    installed=$(compgen -c | grep '^electron[0-9]' | sort -V | tail -1)
    if [ -n "$installed" ]; then
        echo "$(tput setaf 2)Electron successfully installed: $installed$(tput sgr0)"
        return 0
    else
        echo "$(tput setaf 1)!!!!! Electron installation could not be verified !!!!!$(tput sgr0)"
        return 1
    fi
}

# Setup bash
chmod +x ./threadstepper

# Install dependencies
installElectron


echo "Please restart Thread Stepper!"
echo "Please close this window..."