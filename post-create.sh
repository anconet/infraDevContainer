#!/bin/bash
set -xe
sudo apt update

# preseed timezone to prevent tzdata from asking questions during install
sudo apt-get install -y --no-install-recommends debconf-utils
# set timezone file/link early so dpkg knows our choice
echo "America/Chicago" | sudo tee /etc/timezone > /dev/null
sudo ln -fs /usr/share/zoneinfo/America/Chicago /etc/localtime
# debconf selections for tzdata interactive prompts
echo "tzdata tzdata/Areas select America" | sudo debconf-set-selections
echo "tzdata tzdata/Zones/America select Chicago" | sudo debconf-set-selections

DEBIAN_FRONTEND=noninteractive sudo apt install -y --no-install-recommends \
    curl \
    dbus-x11 \
    git \
    python3-pip \
    wget \
    make \
    vim \
    less

# Persist alias for future interactive shells.
#BUILD_ALIAS="alias build='python3 /workspaces/infraVerilogSetupTest/build.py'"
#if ! grep -Fxq "$BUILD_ALIAS" "$HOME/.bashrc"; then
#    echo "$BUILD_ALIAS" >> "$HOME/.bashrc"
#fi