"""
Manages collection of stats for the daily report.
"""

import socket
import smtplib

from .config import Config
import statusreport.gather as gather
import statusreport.formatx as formatx


class Report:

    def __init__(self, config_file):
        self.cfg = Config(config_file)
        self.hostname = socket.gethostname()
        self.fqdn = socket.getfqdn()
        self.sender = f"root@{self.fqdn}"
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

    def dump_info(self):
        """
        Use print to dump content of gathered information.  Debugging usually.
        :return:
        """
        print(self.subject)
        print("Uptime:", self.uptime)
        print("Memory:", self.memory)
        print("Distribution:", self.distribution)
        print("Kernel:", self.kernel)
        print("RootFS Writes:", self.rootfs_writes)
        print("FS Space:", self.fs_space)
        print("FS Inode:", self.fs_inode)
        print("Logged on:", self.logged_on)
        print("Public IP:", self.public_ip)
        print("Raspberry Pi Model:", self.raspberry_pi_model)

    def build_report(self):
        self.body += formatx.uptime(*self.uptime)
        self.body += formatx.memory(*self.memory)
        self.body += formatx.distribution(*self.distribution)
        self.body += formatx.kernel(*self.kernel)
        self.body += formatx.root_fs(*self.rootfs_writes)
        self.body += formatx.fs_space(*self.fs_space)
        self.body += formatx.fs_inode(*self.fs_inode)
        self.body += formatx.logged_on(*self.logged_on)
        self.body += formatx.public_ip(*self.public_ip)
        self.body += formatx.raspberry_pi_model(*self.raspberry_pi_model)

        warn = self.uptime[1] | self.public_ip[1]
        warning = " *** WARNING ***" if warn else ""
        self.subject = f"{socket.gethostname()} Daily Report{warning}"

    def send_report(self):
        message = (f"From: {self.hostname} <{self.sender}>\n"
                   f"To: {self.cfg.envelope_sendto}\n"
                   f"Subject: {self.subject}\n"
                   f"MIME-Version: 1.0\n"
                   f"Content-type: text/html\n\n"
                   f"{self.body}\n")

        smtp = smtplib.SMTP(self.cfg.server)
        smtp.ehlo()
        smtp.starttls()
        smtp.sendmail(self.sender, self.cfg.sendto, message)
        smtp.quit()
