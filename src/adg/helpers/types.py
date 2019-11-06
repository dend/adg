#cSpell:ignore macos
'''
Module responsible for general types
that are used across the application.
'''

from enum import Enum

class OperatingSystem(Enum):
    '''
    Enum containing possible operating system
    variants. These are the supported OSs for
    the adg toolchain.
    '''

    windows = 1
    linux = 2
    macos = 3
    other = 4
