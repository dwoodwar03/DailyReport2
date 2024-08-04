#!/usr/bin/env python3

"""
Application to gather daily status of running server and send as an email report to specified user.
"""

import argparse

from statusreport.report import Report


def main():
    """
    Main function for gathering information for the daily report.
    """

    # Arg Parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="/etc/DailyReport.yaml",
                        help="Custom location of config file")
    parser.add_argument("--reboot-alert", action="store_true", default=False,
                        help="Report caused by reboot")
    parser.add_argument("--no-email", action="store_true", default=False,
                        help="Don't send email")
    args = parser.parse_args()

    # Read Configuration
    builder = Report(args.config, args.reboot_alert)
    builder.gather_info()

    builder.build_report()
    if args.no_email:
        builder.dump_info()
    else:
        builder.send_report()


if __name__ == "__main__":
    main()
