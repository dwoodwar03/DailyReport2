#!/usr/bin/env python3

"""
Manage the configuration file
"""

import yaml


class Config:
    """
    Manage the configuration file for the DailyReport application
    """

    def __init__(self, config_file):
        self._cfg = yaml.safe_load(open(config_file))

    @property
    def server(self):
        return self._cfg['mail']['server']

    @property
    def sendto(self):
        email = [email for _, email in self._cfg['mail']['sendto']]
        return email

    @property
    def envelope_sendto(self):
        content = ""
        seperator = ""
        for full_name, email in self._cfg['mail']['sendto']:
            content += f"{seperator}{full_name} <{email}>"
            seperator = ", "
        return content
