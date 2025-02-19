"""
Manages collection of stats for the daily report.
"""

import socket
import smtplib
from email.message import EmailMessage

from .config import Config
import statusreport.gather as gather
import statusreport.formatx as formatx


class Report:

    def __init__(self, config_file, reboot_alert):
        self.cfg = Config(config_file)
        self.reboot_alert = reboot_alert

        self.hostname = socket.gethostname()
        self.fqdn = socket.getfqdn()
        self.sender = f"root@{self.fqdn}"
        self.report_name = "Reboot Alert" if reboot_alert else "Daily Report"
        self.body = ""

        self.subject = None
        self.uptime = None
        self.memory = None
        self.distribution = None
        self.kernel = None
        self.rootfs_writes = None
        self.fs_space = None
        self.fs_inode = None
        self.logged_on = None
        self.public_ip = None
        self.raspberry_pi_model = None
        self.raid_status = None
        self.local_ip = None
        self.backup_log = None
        self.reboot_required = None

    def gather_info(self):
        self.uptime = gather.uptime_seconds()
        # boot time calculated from uptime in seconds.
        self.memory = gather.memory_usage()
        self.distribution = gather.distribution()
        self.kernel = gather.kernel()
        self.rootfs_writes = gather.rootfs_writes()
        self.fs_space = gather.fs_space()
        self.fs_inode = gather.fs_inode()
        self.logged_on = gather.logged_on()
        self.public_ip = gather.public_ip()
        self.raspberry_pi_model = gather.raspberry_pi_model()
        self.raid_status = gather.raid_status()
        self.local_ip = gather.local_ip()
        self.backup_log = gather.backup_log()
        self.reboot_required = gather.reboot_required()

    def dump_info(self):
        """
        Use print to dump content of gathered information.  Debugging usually.
        :return:
        """
        print(self.subject)
        print("Uptime:", self.uptime)
        print("Reboot required:", self.reboot_required)
        print("Memory:", self.memory)
        print("Distribution:", self.distribution)
        print("Kernel:", self.kernel)
        print("RootFS Writes:", self.rootfs_writes)
        print("FS Space:", self.fs_space)
        print("FS Inode:", self.fs_inode)
        print("Logged on:", self.logged_on)
        print("Public IP:", self.public_ip)
        print("Raspberry Pi Model:", self.raspberry_pi_model)
        print("RAID Status:", self.raid_status)
        print("Local IP:", self.local_ip)

    def build_report(self):

        warn = self.public_ip[1] | self.raid_status[1] | self.local_ip[1] | self.backup_log[1] | self.reboot_required[1]

        # Do not set warning on uptime if this is a reboot alert.
        if self.reboot_alert:
            self.body += formatx.uptime(self.uptime[0], False)
        else:
            self.body += formatx.uptime(*self.uptime)
            warn = warn | self.uptime[1]

        warning = " *** WARNING ***" if warn else ""
        self.subject = f"{socket.gethostname()} {self.report_name}{warning}"

        self.body += formatx.reboot_required(*self.reboot_required)
        self.body += formatx.memory(*self.memory)
        self.body += formatx.distribution(*self.distribution)
        self.body += formatx.kernel(*self.kernel)
        self.body += formatx.root_fs(*self.rootfs_writes)
        self.body += formatx.fs_space(*self.fs_space)
        self.body += formatx.fs_inode(*self.fs_inode)
        self.body += formatx.logged_on(*self.logged_on)
        self.body += formatx.local_ip(*self.local_ip)
        self.body += formatx.public_ip(*self.public_ip)
        self.body += formatx.raspberry_pi_model(*self.raspberry_pi_model)
        self.body += formatx.raid_status(*self.raid_status)
        self.body += formatx.backup_log(*self.backup_log)

    def send_report(self):

        smtp = smtplib.SMTP(self.cfg.server)

        email = EmailMessage()
        email.set_content(self.body, subtype="html")
        email["To"] = self.cfg.envelope_sendto
        email["From"] = f"{self.hostname} <{self.sender}>"
        email["Subject"] = self.subject
        smtp.send_message(email)

        smtp.quit()
