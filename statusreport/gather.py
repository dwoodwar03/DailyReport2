"""
Holds functions which gather information about the system.
"""

import apt
import json
import netifaces
import os
import re
import shlex
import subprocess
import urllib.request
import yaml

from pathlib import Path
from datetime import datetime

pi_models_file = Path(os.path.dirname(__file__)) / "pi_models.yaml"
pi_models: dict = yaml.safe_load(open(pi_models_file))


def get_info(command):
    """
    Returns output from command which is run.
    """

    cmd_output = ""
    try:
        cmd_output = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE
            ).communicate()[0].decode("utf-8")
    except OSError as err:
        if err.errno != 2:
            cmd_output = "ERROR - %d - %s" % (err.errno, err.strerror)

    return cmd_output


def grep(file, pattern):
    """
    Returns list of results when searching provided filename and regexp pattern.
    :param file:
    :param pattern:
    :return:
    """
    results = []
    find = re.compile(pattern)

    with open(file) as f:
        for line in f:
            found = find.search(line)
            if found:
                results.append(found.group(1))

    return results


def uptime_seconds():
    """
    Gets the uptime of the server
    :return:
    """
    with open('/proc/uptime', 'r') as f:
        seconds = float(f.readline().split()[0])

    # days = int(seconds // 86400)
    # seconds = seconds - (days * 86400)
    # hours = int(seconds // 3600)
    # seconds = seconds - (hours * 3600)
    # minutes = int(seconds // 60)
    # seconds = seconds - (minutes * 60)

    warn = True if seconds < 86400 else False
    # return f"{days} days {hours:02}:{minutes:02}:{seconds:05.2f}", warn
    return seconds, warn


def memory_usage():
    """
    Gets the memory usage of the server
    :return:
    """
    return get_info("free -h"), False


def distribution():
    """
    Gets the distribution details of the server
    :return:
    """
    return get_info("lsb_release -d -c"), False


def kernel():
    """
    Gets the kernel version of the server
    :return:
    """
    return get_info("uname -snrvmo"), False


def rootfs_writes():
    """
    Get the amount of writes performed in root filesystem.
    Might not be accurate if the device crashes though.
    :return:
    """

    dev_name = get_info("findmnt / --output=source --noheadings").strip()
    root_dev_name = dev_name.split("/")[2]

    try:
        with open(f"/sys/fs/ext4/{root_dev_name}/lifetime_write_kbytes", "r") as f:
            lifetime_writes = int(f.read())
    except FileNotFoundError:
        lifetime_writes = -1

    return (dev_name, lifetime_writes), False


def fs_space():
    """
    Gets the amount of free space on the file systems.
    :return:
    """
    return get_info("df -h -x devtmpfs -x tmpfs -x squashfs -x efivarfs"), False


def fs_inode():
    """
    Gets the amount of free inodes on the file systems.
    :return:
    """
    return get_info("df -i -x devtmpfs -x tmpfs -x squashfs -x efivarfs"), False


def logged_on():
    """
    Gets list of logged on users.
    :return:
    """
    return get_info("who"), False


def public_ip():
    """
    Gets the public IP address which the server uses for outbound internet communications.
    :return:
    """
    warn = False
    try:
        request = urllib.request.urlopen('http://httpbin.org/ip')
        result = request.read().decode("utf-8")
        ip_addr = json.loads(result)['origin']
    except: # TODO Make more explicit.
        ip_addr = "* NETWORK ERROR *"
        warn = True

    return ip_addr, warn


def raspberry_pi_model():
    pi_model = grep("/proc/cpuinfo", r'^Revision.*: (.*)$')
    warn = False
    version = ""

    if pi_model:
        version = pi_models.get(pi_model[0])
        if not version:
            warn = True
            version = f"** UNKNOWN PI: {pi_model[0]} **"

    return version, warn


def raid_status():
    warn = False
    raid_device = grep("/proc/mdstat", r'^(md[0-9]*)')

    if not raid_device:
        return None, False

    # Not a PI.
    if len(raid_device) > 2:
        return f"Multiple Devices Found: {raid_device}", False

    # Possibly badly broken mirror.
    if len(raid_device) == 2:
        return f"Multiple Devices Found: {raid_device}", True

    current_raid_status = grep("/proc/mdstat", r'blocks .*\[.*\] \[(.*)\]')[0]
    if "_" in current_raid_status:
        warn = True

    content = get_info(f"mdadm --query --detail /dev/{raid_device[0]}")

    return content, warn


def local_ip():
    interface_details = {}
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        if interface == "lo":
            continue
        detail = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
        if detail:
            interface_details[interface] = detail

    if not interface_details:
        return "", True

    return interface_details, False


def backup_log():
    """
    Return "Backup not enabled" if /etc/cron.d/Backup does not exist., warning = False
    If backup file does not exist, Return "Missing Backup Log", warning = True
    If backup file does exist and > 1 day old Return "Backup not run in 24 hrs", warning = True
    If backup file does exist and is empty, Return "Backup Log is empty", warning = True
    Return content of Log, Warning = False

    :return:
    """

    enabled = Path("/etc/cron.d/Backup").exists()
    if not enabled:
        return "Backup not enabled", False

    backup_log_file = Path("/var/log/backup.log")
    if not backup_log_file.exists():
        return "Missing Backup Log or Backup has never run", True

    if backup_log_file.stat().st_size == 0:
        return "Backup Log is empty - Likely Backup Failed", True

    log_file_age_days = (datetime.timestamp(datetime.now()) - backup_log_file.stat().st_mtime) / 86400
    if log_file_age_days > 1:
        return f"Backup last run {log_file_age_days:.0f} days ago", True

    return backup_log_file.read_text(), False

def reboot_required():
    """
    Returns list of packages which requires a reboot to be fully installed.
    True is returned meaning reboot is required.
    False is returned meaning reboot is not required.
    :return:
    """
    required = Path("/var/run/reboot-required").exists()
    package_list = Path("/var/run/reboot-required.pkgs")
    packages = ""

    if required:
        if package_list.exists():
            packages = package_list.read_text()
        return packages, True
    else:
        return packages, False

def package_status():
    """
    Returns list of packages which are available to be upgraded.
    :return:
    """

    detail = []

    for pkg in apt.Cache():
        if pkg.is_upgradable:
            detail.append({
                "name": pkg.shortname,
                "from": pkg.installed.version,
                "to": pkg.candidate.version,
                "summary": pkg.installed.summary
            })

    return detail, False

def monitor_sync():
    sync_status_file = Path("/var/log/monitor-sync-state.yaml")

    if not sync_status_file.exists():
        return None, False

    content = sync_status_file.read_text()
    if content.count("OK") < 2:
        return "Issues exist with Monitor Sync Checker", True

    return "Monitor Sync Checker is OK", False