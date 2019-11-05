# cSpell:ignore shutil, dtemp, dbin, docfx, dsite, venv, macos

import os
import shutil
from urllib.parse import urlparse
from .types import OperatingSystem
from .systemhelper import SystemHelper
import urllib.request
import subprocess
import re
import zipfile
import io
import shutil
import json
import venv

virtual_environment_directory = "dtemp"

class Validator(object):
    @staticmethod
    def validate_url(url):
        # This is taken from Stack Overflow: https://stackoverflow.com/a/7160778
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return re.match(regex, url) is not None

class LibraryInstaller(object):
    @staticmethod
    def install_python_library(library):
       print(f"[info] Installing {library}...")
       pip_path = os.path.join(virtual_environment_directory, "bin", "pip")
       subprocess.call([pip_path, "install", library])
            
    @staticmethod
    def create_environment():
        print (f'[info] Bootstrapping the virtual environment...')
        venv.create(virtual_environment_directory, with_pip=True)

class PresenceVerifier(object):
    @staticmethod
    def docfx_exists(auto_install):
        if (os.path.exists('dbin/docfx/docfx.exe')):
            return True
        else:
            if auto_install:
                print('[info] Downloading and extracting DocFX...')
                urllib.request.urlretrieve("https://github.com/dotnet/docfx/releases/download/v2.42.4/docfx.zip", "temp_docfx.zip")
                with zipfile.ZipFile("temp_docfx.zip", "r") as zip_ref:
                    zip_ref.extractall("dbin/docfx")
                return True
            return False

    @staticmethod
    def shell_command_exists(command):
        return shutil.which(command) is not None

class LibraryProcessor(object):
    @staticmethod
    def process_libraries(libraries, platform, docpath):
        if (platform.lower() == 'python'):
            for library in libraries:
                if (Validator.validate_url(library)):
                    try:
                        url_parse_result = urlparse(library)
                        domain = url_parse_result.netloc
                        if (domain.lower().endswith('github.com')):
                            print (f'[info] Getting {library} from GitHub...')
                        else:
                            print (f'[info] Getting {library} from a direct source...')
                    except:
                        print ('[error] Could not install library from source.')
                        # Not a URL, so we should try taking this as a PyPI package.
                else:
                    LibraryInstaller.create_environment()

                    LibraryInstaller.install_python_library(library)

                    # TODO: Need to implement a check that verifies whether the library was really installed.
                    LibraryDocumenter.document_python_library(library, docpath)
                    
                    # Perform cleanup and just remove the folder where the virtual environment was set up.
                    #shutil.rmtree('dtemp')

class LibraryDocumenter(object):
    @staticmethod
    def document_python_library(library, docpath):
        print (f'[info] Attempting to document {library} from PyPI.')
        true_docpath = docpath
        if not docpath:
            true_docpath = os.getcwd()

        # Make sure that we install the documentation pre-requisites. These are the tools that will generate the final output.
        LibraryInstaller.install_python_library("sphinx-docfx-yaml")

        target_documentation_directory = os.path.join(virtual_environment_directory, "_documentation")
        if not os.path.exists(target_documentation_directory):
            os.mkdir(target_documentation_directory)

        target_sphinx_directory = os.path.join(target_documentation_directory, "_sphinx")
        if not os.path.exists(target_sphinx_directory):
            os.mkdir(target_sphinx_directory)
        
        target_docfx_directory = os.path.join(target_documentation_directory, "_docfx")
        if not os.path.exists(target_docfx_directory):
            os.mkdir(target_docfx_directory)
        
        # "sphinx-quickstart", "-q", "-p", "'adg'", "-a", "'automated'", "-v", "'1.0'" 
        sphinx_quickstart_path = os.path.join("bin", "sphinx-quickstart")
        print(subprocess.check_output("cd " + target_sphinx_directory + f" && ./../../{sphinx_quickstart_path} -q -p 'adg' -a 'automated' -v '1.0'", shell=True))

    @staticmethod
    def document_node_library(library, docpath):
        true_docpath = docpath
        if not docpath:
            true_docpath = os.getcwd()

        #process_result = subprocess.run(['pip3', 'list',], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

class ConsoleUtil(object):
    @staticmethod
    def pretty_stdout(stdout):
        output = str(stdout)
        output = output.split('\\n')
        for x in range(len(output)):
            print (output[x])