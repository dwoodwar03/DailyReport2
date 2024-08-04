#!/usr/bin/env bash

# Install DailyReport2

# Needs to run as root to perform the installation.
if [ $EUID -ne 0 ]; then
		echo "This setup tool is required to run as root"
		exit
fi

INSTALL_DIR=/usr/local/DailyReport2
INSTALL_LIB_DIR=${INSTALL_DIR}/statusreport
UPGRADE=FALSE
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ ! -d $INSTALL_DIR ]; then
	echo "Creating Folder: $INSTALL_DIR"
	mkdir "$INSTALL_DIR"
fi

if [ ! -d $INSTALL_LIB_DIR ]; then
	echo "Creating Folder: $INSTALL_LIB_DIR"
	mkdir "$INSTALL_LIB_DIR"
fi

echo Installing application....
cp "${SCRIPT_DIR}"/*.py $INSTALL_DIR
cp "${SCRIPT_DIR}"/statusreport/*.py $INSTALL_LIB_DIR

if [ ! -f /etc/DailyReport.yaml ]; then
    echo "Copying DailyReport.yaml config file"
    cp "${SCRIPT_DIR}"/etc/DailyReport.yaml.template /etc/DailyReport.yaml
else
    echo "Copying DailyReport.yaml config file as /etc/DailyReport.yaml.upgrade"
    cp "${SCRIPT_DIR}"/etc/DailyReport.yaml.template /etc/DailyReport.yaml.upgrade
    UPGRADE=TRUE
fi

echo "Copying DailyReport Cron Job"
cp "${SCRIPT_DIR}"/etc/cron.d/DailyReport /etc/cron.d/

echo "Making files executable"
chmod +x "${INSTALL_DIR}"/*.py
echo

if [ $UPGRADE = FALSE ]; then
    echo "Installation Complete"
    echo "Please configure /etc/DailyReport.json"
else
    echo "Upgrade Complete"
fi