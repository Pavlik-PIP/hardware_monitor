#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .hardware_logger import HardwareLogger

import sys
import argparse
import platform
import os
from enum import IntEnum

class Interval(IntEnum):
    M10  = 60*10
    HOUR = 60*60
    DAY  = 60*60*24

def main():
    if platform.system() != "Linux":
        sys.exit("Your system is not supported")

    choices_description = \
"""Possible values of T:
  m10  - 10 minutes
  hour - one hour
  day  - one day"""

    parser = argparse.ArgumentParser(description="Log system info at "
            "specified interval", epilog=choices_description,
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("interval", metavar="interval", nargs='?',
                        choices=["m10", "hour", "day"], default="m10",
                        help="interval of time (default: %(default)s)")

    args = parser.parse_args()

    interval = Interval[args.interval.upper()]
    config = os.path.join(os.path.realpath(__package__), "config",
                          "hardware_boundaries.json")
    
    logger = HardwareLogger(interval, config)
    logger.start()

    try:
        input("Press Enter to stop...")
    except KeyboardInterrupt:
        print()

    logger.stop()

if __name__ == "__main__":
    main()
