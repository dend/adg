# cSpell:ignore coreutil, macos, docfx

'''
Module responsible for taking user input and deciding
what to do with it.
'''

from .core import LibraryProcessor, Util
from .types import OperatingSystem

class CommandProcessor():
    '''
    Class that processes commands received from the terminal.
    '''

    @staticmethod
    def validate(command, operating_system):
        '''Validates the command line input from the user.'''

        if command.commands_parser == 'make':
            print('[info] Making documentation.')

            if (command.library is not None) and (command.platform is not None):
                print("[info] All requirements ready.")

                if operating_system in (OperatingSystem.macos, OperatingSystem.linux):
                    if not Util.shell_command_exists('mono'):
                        print("[info] Your system requires the Mono framework. It was not found.")

                print(f"[info] Collecting information on {len(command.library)} libraries...")

                LibraryProcessor.process_libraries(command.library,
                                                   command.platform, command.out,
                                                   operating_system, command.format)
            else:
                print("[error] You need to specify required parameters. Aborting.")
