import os
import shutil

class PresenceVerifier(object):
    @staticmethod
    def docfx_exists():
        if (os.path.exists('dbin/docfx/docfx.exe')):
            return True
        else:
            return False

    @staticmethod
    def mono_exists():
        return shutil.which('mono') is not None