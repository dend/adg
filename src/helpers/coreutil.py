import os
import shutil
from urllib.parse import urlparse

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

class LibraryProcessor(object):
    @staticmethod
    def process_libraries(libraries, platform):
        if (platform.lower() == 'python'):
            for library in libraries:
                try:
                    url_parse_result = urlparse(library)
                    domain = url_parse_result.netloc
                    if (domain.lower().endswith("github.com")):
                        print (f'[info] Getting the {library} from GitHub...')
                except:
                    print (f'[info] The {library} is not a direct pointer - attempting to read from PyPI.')
                    # Not a URL, so we should try taking this as a PyPI package.
