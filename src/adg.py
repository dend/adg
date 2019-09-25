#!/usr/bin/env python3
#cSpell:ignore nargs, macos, cygwin

from sys import argv
from helpers.types import OperatingSystem
from helpers.commandprocessor import CommandProcessor
from helpers.systemhelper import SystemHelper
import argparse

parser = argparse.ArgumentParser(description='adg - version 1.0.2-june-2019')

subparsers = parser.add_subparsers(dest="commands_parser")
make_parser = subparsers.add_parser('make')

make_parser.add_argument('--library', metavar='L', type=str, nargs='+',
                   help='A single or space-separated list of libraries to document.')
make_parser.add_argument('--platform', type=str, metavar='P',
                   help='Target platform for the documented library.')
make_parser.add_argument('--out', type=str, metavar='O',
                   help='Output path for the generated documentation.')
make_parser.add_argument('--auto-install', type=bool, metavar='A',
                   help='Determines whether helper tools need to be installed automatically.')

args = parser.parse_args()

# Check for the operating system. This will determine how we handle
# CLI commands being passed to the DocFX tooling.

current_os = SystemHelper.get_operating_system()

print ('[info] Operating environment: ', current_os)

# Check for command line arguments and verify the integrity of those.

if (not len(argv) > 1):
    print('[error] No command line arguments supplied to the CLI. Terminating.')
else:
    CommandProcessor.validate(args, current_os)