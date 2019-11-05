# cSpell:ignore coreutil, macos, docfx

from .coreutil import LibraryProcessor, PresenceVerifier
from .types import OperatingSystem

class CommandProcessor(object):
    @staticmethod
    def validate(command, platform):
        if (command.commands_parser == 'make'):
            print ('[info] Making documentation.')

            if (command.library is not None) and (command.platform is not None):
                print ('[info] Requirements specified in command prompt. Proceeding to resource assessment...')

                if (platform == OperatingSystem.macos) or (platform == OperatingSystem.linux):
                    if (not PresenceVerifier.shell_command_exists('mono')):
                        print ('[info] You are running on a system that requires the Mono framework installed, and it was not found. You might not be able to document .NET packages properly.')
                
                print (f'[info] Collecting information on {len(command.library)} libraries...')

                LibraryProcessor.process_libraries(command.library, command.platform, command.out)
            else:
                print ('[error] You need to specify --platform, --library and --out to generate documentation.')