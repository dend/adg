#!/usr/bin/env python3

from sys import platform, argv
from helpers.types import *
from helpers.commandprocessor import *
import argparse

parser = argparse.ArgumentParser(description='adg - version 1.0.21-jan-2019')

subparsers = parser.add_subparsers(dest="commands_parser")
make_parser = subparsers.add_parser('make')

make_parser.add_argument('--library', metavar='L', type=str, nargs='+',
                   help='A single or space-separated list of libraries to document.')
make_parser.add_argument('--platform', type=str, metavar='P',
                   help='Target platform for the documented library.')
make_parser.add_argument('--out', type=str, metavar='O',
                   help='Output path for the generated documentation.')

args = parser.parse_args()

# Check for the operating system. This will determine how we handle
# CLI commands being passed to the DocFX tooling.

current_os = OperatingSystem.other

if platform == "linux" or platform == "linux2":
    current_os = OperatingSystem.linux
elif platform == "darwin":
    current_os = OperatingSystem.macos
elif platform == "win32" or platform == "cygwin":
    current_os = OperatingSystem.windows

print ('[info] Operating environment: ', current_os)

# Check for command line arguments and verify the integrity of those.

if (not len(argv) > 1):
    print('[error] No command line arguments supplied to the CLI. Terminating.')
else:
    CommandProcessor.validate(args, current_os)