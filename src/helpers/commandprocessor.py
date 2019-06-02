from helpers.coreutil import *
from helpers.types import *

class CommandProcessor(object):
    @staticmethod
    def validate(command, platform):
        if (command.commands_parser == 'make'):
            print ('[info] Making documentation.')

            if (command.library is not None) and (command.platform is not None):
                print ('[info] Requirements specified in command prompt. Proceeding to resource assessment...')
                if (PresenceVerifier.docfx_exists(command.auto_install)):
                    print ('[info] DocFX is available.')
                    if (platform == OperatingSystem.macos) or (platform == OperatingSystem.linux):
                        if (not PresenceVerifier.shell_command_exists('mono')):
                            print ('[error] You are running on a system that requires the Mono framework installed, and it was not found.')
                    
                    print (f'[info] Collecting information on {len(command.library)} libraries...')

                    LibraryProcessor.process_libraries(command.library, command.platform, command.out)
                else:
                    print ('[error] Could not find DocFX locally. Please verify that the package was properly installed.')
            else:
                print ('[error] You need to specify --platform, --library and --out to generate documentation.')