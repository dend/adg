#cSpell:ignore nargs, macos, cygwin

import argparse
from sys import argv
from adg.helpers.commandprocessor import CommandProcessor
from adg.helpers.core import Util

PARSER = argparse.ArgumentParser(description='adg - version 1.0.9-november-2019')
SUB_PARSERS = PARSER.add_subparsers(dest="commands_parser")
MAKE_PARSER = SUB_PARSERS.add_parser('make')

MAKE_PARSER.add_argument('--library', metavar='L', type=str, nargs='+',
                         help='Library that needs to be documented.')
MAKE_PARSER.add_argument('--platform', type=str, metavar='P',
                         help="""Target platform for the documented library.
                         Acceptable values: python""")
MAKE_PARSER.add_argument('--out', type=str, metavar='O',
                         help='Output path for the generated documentation.')
MAKE_PARSER.add_argument('--format', type=str, metavar='F',
                         help="""Output format for the documentation.
                         Acceptable values: yaml, html.""")

ARGS = PARSER.parse_args()

# Check for the operating system. This will determine how we handle
# CLI commands being passed to the DocFX tooling.

CURRENT_OS = Util.get_operating_system()

print('[info] Operating environment: ', CURRENT_OS)

# Check for command line arguments and verify the integrity of those.

if len(argv) <= 1:
    print('[error] No command line arguments supplied to the CLI. Terminating.')
else:
    CommandProcessor.validate(ARGS, CURRENT_OS)
