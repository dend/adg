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
        # process_result = subprocess.run(['python', 'install', '-t', 'dtemp/packages', library], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # print(process_result.stdout)

        os = SystemHelper.get_operating_system()

        if (os == OperatingSystem.macos) or (os == OperatingSystem.linux):
            print('[info] Starting the virtual environment...')
            process_result = subprocess.run(['source', 'dtemp/bin/activate'], executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print(process_result.stdout)
        else:
            print ('[info] Virtual environment activation is not yet implemented for Windows.')

        # Check if we're running inside a virtual environment. If this is not the case, we need to avoid processing.
        if hasattr(sys, 'base_prefix'):
            print(f'[info] Running inside virtual {sys.prefix} environment.')
            
    @staticmethod
    def create_environment():
        print('[info] Creating a local virtual environment...')
        process_result = subprocess.run(['python', '-m', 'venv', 'dtemp'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(process_result.stdout)

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
            if (PresenceVerifier.shell_command_exists('pip3')):
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
                        print (f'[info] Bootstrapping the virtual environment...')
                        LibraryInstaller.create_environment()

                        print (f'[info] The {library} is not a direct pointer - attempting to read from PyPI.')
                        LibraryInstaller.install_python_library(library)

                        # TODO: Need to implement a check that verifies whether the library was really installed.
                        LibraryDocumenter.document_python_library(library, docpath)
                        shutil.rmtree('dtemp')
            else:
                print ('[error] Could not find an installed pip3 tool. Make sure that Python tooling is installed if you are documenting Python packages.')

class LibraryDocumenter(object):
    @staticmethod
    def document_python_library(library, docpath):
        true_docpath = docpath
        if not docpath:
            true_docpath = os.getcwd()

        process_result = subprocess.run(['pip3', 'list',], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if 'spinx-docfx-yaml' in process_result.stdout.decode('utf-8'):
            # We have the extension (https://github.com/docascode/sphinx-docfx-yaml) installed
            print ('[info] The sphinx-docfx-yaml extension is already installed.')
        else:
            print ('[info] Installing sphinx-docfx-yaml...')
            process_result = subprocess.run(['pip3', 'install', 'sphinx-docfx-yaml', '--user'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            ConsoleUtil.pretty_stdout(process_result.stdout)

        print (f'[info] Processing documentation for {library}...')
        process_result = subprocess.run(['sh', 'scripts/pythondoc.sh', 'dtemp/packages', library.replace('-','/'), os.path.abspath(true_docpath)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ConsoleUtil.pretty_stdout(process_result.stdout)        

class ConsoleUtil(object):
    @staticmethod
    def pretty_stdout(stdout):
        output = str(stdout)
        output = output.split('\\n')
        for x in range(len(output)):
            print (output[x])