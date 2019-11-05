from sys import platform
from .types import OperatingSystem

class SystemHelper(object):
    @staticmethod
    def get_operating_system():
        if platform == "linux" or platform == "linux2":
            return OperatingSystem.linux
        elif platform == "darwin":
            return OperatingSystem.macos
        elif platform == "win32" or platform == "cygwin":
            return OperatingSystem.windows
        else:
            return OperatingSystem.other