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
    parser.add_argument("--config", help="Custom location of config file")
    args = parser.parse_args()

    # Read Configuration
    builder = Report(args.config if args.config else "/etc/DailyReport.yaml")
    builder.gather_info()

    # builder.dump_info()
    builder.build_report()
    builder.send_report()


if __name__ == "__main__":
    main()
