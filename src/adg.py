from sys import platform
from helpers.types import *

print ('adg - version 1.0.21-jan-2019')

current_os = OperatingSystem.other

if platform == "linux" or platform == "linux2":
    current_os = OperatingSystem.linux
elif platform == "darwin":
    current_os = OperatingSystem.macos
elif platform == "win32" or platform == "cygwin":
    current_os = OperatingSystem.windows

print ('Operating environment: ', current_os)