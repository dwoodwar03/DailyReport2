"""
Used to format the different types of output for the email report.
"""

import datetime


def format_html(title, content, warn):
    if warn:
        title += " - ** WARNING **"

    output = (f"<B><U>{title}</U></B>\n"
              f"<PRE>\n"
              f"{content}"
              f"</PRE>\n")
    return output


def uptime(uptime_secs, warn):
    """
    Returns a formatted string of the uptime.
    :return:
    """

    # Calculate formatted uptime from uptime in seconds.
    days = int(uptime_secs // 86400)
    seconds = uptime_secs - (days * 86400)
    hours = int(seconds // 3600)
    seconds = seconds - (hours * 3600)
    minutes = int(seconds // 60)
    seconds = seconds - (minutes * 60)
    uptime_text = f"{days} days {hours:02}:{minutes:02}:{seconds:05.2f}"

    # Calculate Boot Time
    uptime_delta = datetime.timedelta(seconds=uptime_secs)
    today = datetime.datetime.now()
    formatstring = "%a %d %b %Y %H:%M:%S %Z"
    boot_time = (today - uptime_delta).strftime(formatstring)
    report_time = today.strftime(formatstring)

    uptime_secs = (f"System Uptime          : {uptime_text}\n"
                   f"System Boot time       : {boot_time}\n"
                   f"Report Generation Time : {report_time}\n")

    return format_html("System Uptime", uptime_secs, warn)


def memory(content, warn):
    return format_html("Memory Usage", content, warn)


def distribution(content, warn):
    return format_html("Distribution Details", content, warn)


def kernel(content, warn):
    return format_html("Kernel Details", content, warn)


def root_fs(rootfs, warn):
    content = f"{rootfs[0]} {rootfs[1]:,}"
    return format_html("Root FS Writes Details", content, warn)


def fs_space(space, warn):
    return format_html("FS Space Details", space, warn)


def fs_inode(inode, warn):
    return format_html("FS Inode Details", inode, warn)


def logged_on(logged, warn):
    return format_html("Logged On Details", logged, warn)


def public_ip(ip, warn):
    return format_html("Public IP Details", ip, warn)


def raspberry_pi_model(model, warn):
    if model:
        return format_html("Raspberry Pi Model Details", model, warn)
    return ""


def raid_status(raid, warn):
    if raid:
        return format_html("Raid Status Details", raid, warn)
    return ""

