# cSpell:ignore shutil, dtemp, dbin, docfx, dsite
# cSpell:ignore venv, macos, rmtree, folderize, getcwd, mkdir, isdir, isfile

'''
Module responsible for the processing of user input
and generating the documentation for specified
libraries.
'''

import os
import shutil
import urllib.request
import subprocess
import re
import zipfile
import venv
import sys
from urllib.parse import urlparse
from distutils.dir_util import copy_tree
from .types import OperatingSystem
import re

VIRTUAL_ENVIRONMENT_DIRECTORY = "dtemp"
DOCFX_FILE_NAME = "temp_docfx.zip"
BINARY_DIRECTORY = "dbin"

class LibraryInstaller():
    '''
    Class that is responsible for installing libraries that
    need to be documented.
    '''

    @staticmethod
    def install_python_library(library, operating_system):
        '''Installs a Python library to document.'''

        print(f"[info] Installing {library}...")

        python_path = ''
        if operating_system in (OperatingSystem.macos, OperatingSystem.linux):
            python_path = os.path.join(VIRTUAL_ENVIRONMENT_DIRECTORY, "bin", "python")
        elif operating_system == OperatingSystem.windows:
            python_path = os.path.join(VIRTUAL_ENVIRONMENT_DIRECTORY, "Scripts", "python")
        else:
            return

        subprocess.call([python_path, "-m", "pip", "install", library])

    @staticmethod
    def create_environment():
        '''Creates a Python virtual environment.'''

        print(f'[info] Bootstrapping the virtual environment...')
        venv.create(VIRTUAL_ENVIRONMENT_DIRECTORY, with_pip=True)

class LibraryProcessor():
    '''
    Class that is responsible for processing the libraries that
    need to be documented. This is where the documentation
    is actually produced.
    '''

    @staticmethod
    def process_libraries(libraries, platform, docpath, operating_system, out_format='yaml'):
        '''Determine the right path for each library being documented.'''

        if platform.lower() == 'python':
            for library in libraries:
                if Util.validate_url(library):
                    try:
                        url_parse_result = urlparse(library)
                        domain = url_parse_result.netloc
                        if domain.lower().endswith('github.com'):
                            print(f'[info] Getting {library} from GitHub...')
                        else:
                            print(f'[info] Getting {library} from a direct source...')
                    except Exception as exception:
                        print(f'[error] Could not install library from source. Error: {exception}')
                        # Not a URL, so we should try taking this as a PyPI package.
                else:
                    LibraryInstaller.create_environment()

                    LibraryInstaller.install_python_library(library, operating_system)

                    # TODO: Need to implement a check that verifies whether
                    # the library was really installed.
                    LibraryProcessor.document_python_library(library, docpath, operating_system, out_format)

    @staticmethod
    def document_python_library(library, docpath, operating_system, out_format='yaml'):
        '''Outputs documentation files for a Python library.'''

        print(f'[info] Attempting to document {library} from PyPI.')
        true_docpath = docpath
        if not docpath:
            true_docpath = os.getcwd()

        if not os.path.exists(true_docpath):
            os.mkdir(true_docpath)

        # Make sure that we install the documentation pre-requisites.
        # These are the tools that will generate the final output.
        LibraryInstaller.install_python_library("sphinx-docfx-yaml", operating_system)

        python_package_folder = os.listdir(os.path.join(VIRTUAL_ENVIRONMENT_DIRECTORY, "lib"))[0]
        print(f"Package folder: {python_package_folder}")

        target_site_packages_directory = ''
        if operating_system in (OperatingSystem.macos, OperatingSystem.linux):
            target_site_packages_directory = os.path.join(VIRTUAL_ENVIRONMENT_DIRECTORY,
                                                        "lib", python_package_folder, "site-packages")
        elif operating_system == OperatingSystem.windows:
            target_site_packages_directory = os.path.join(VIRTUAL_ENVIRONMENT_DIRECTORY,
                                                        "lib", python_package_folder)

        target_library_directory = os.path.join(target_site_packages_directory,
                                                Util.folderize_package_name(library))
        target_docfx_yaml_directory = os.path.join(target_library_directory, "_build", "docfx_yaml")

        print(f"Target folder library: {target_library_directory}")
        print(f"Operating in: {os.getcwd()}")

        if operating_system in (OperatingSystem.macos, OperatingSystem.linux):
            print(Util.pretty_stdout(subprocess.check_output(
                "cd " + target_library_directory + f" && ./../../../../../{os.path.join('bin', 'sphinx-quickstart')} -q -p 'adg' -a 'automated' -v '1.0'", shell=True)))
        elif operating_system == OperatingSystem.windows:
            print(Util.pretty_stdout(subprocess.check_output(
                "cd " + target_library_directory + f" ; & ..\\..\\..\\..\\{os.path.join('Scripts', 'sphinx-quickstart.exe')} -q -p 'adg' -a 'automated' -v '1.0'", shell=True)))

        # We need to update the configuration file for Sphinx,
        # to make sure that we're documenting the right library.
        configuration_file = os.path.join(target_library_directory, "conf.py")
        filedata = ''
        with open(configuration_file, 'r') as file:
            filedata = file.read()

        filedata = filedata.replace("extensions = []",
                                    "extensions = ['sphinx.ext.autodoc', 'docfx_yaml.extension']")

        import_combination = "import os\nimport sys\n"

        directories = [x for x in os.listdir(target_site_packages_directory)
                       if os.path.isdir(os.path.join(target_site_packages_directory, x))]

        for directory in directories:
            if not directory.startswith("_"):
                import_combination += f"sys.path.append(os.path.abspath('../../{directory}'))\n"

        filedata = filedata.replace("# import os", import_combination)

        with open(configuration_file, 'w') as file:
            file.write(filedata)

        if operating_system in (OperatingSystem.macos, OperatingSystem.linux):
            print(Util.pretty_stdout(subprocess.check_output(
                "cd " + target_library_directory + f' && ./../../../../../{os.path.join("bin", "sphinx-apidoc")} . -o . --module-first --no-headings --no-toc --implicit-namespaces',
                shell=True)))
            print(Util.pretty_stdout(subprocess.check_output(
                "cd " + target_library_directory + f' && ./../../../../../{os.path.join("bin", "sphinx-build")} . _build', shell=True)))
        elif OperatingSystem.windows:
            print(Util.pretty_stdout(subprocess.check_output(
                "cd " + target_library_directory + f' ; & ..\\..\\..\\..\\{os.path.join("Scripts", "sphinx-apidoc.exe")} . -o . --module-first --no-headings --no-toc --implicit-namespaces',
                shell=True)))
            print(Util.pretty_stdout(subprocess.check_output(
                "cd " + target_library_directory + f' ; & ..\\..\\..\\..\\{os.path.join("Scripts", "sphinx-build.exe")} . _build', shell=True)))

        # .lower() should likely be enough for a case-insensitive check since we are
        # working with a limited set of values. Otherwise, we would need to check .casefold().
        if out_format.lower() == 'yaml':
            src_files = os.listdir(target_docfx_yaml_directory)
            for file_name in src_files:
                full_file_name = os.path.join(target_docfx_yaml_directory, file_name)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, docpath)
        elif out_format.lower() == 'html':
            if Util.docfx_exists(auto_install=True):
                # DocFX exists. We can proceed.
                if operating_system in (OperatingSystem.macos, OperatingSystem.linux):
                    print(Util.pretty_stdout(subprocess.check_output(
                        "cd " + docpath + " && mono ./../dbin/docfx/docfx.exe init -q", shell=True)))
                elif operating_system == OperatingSystem.windows:
                    print(Util.pretty_stdout(subprocess.check_output(
                        "cd " + docpath + " ; & ..\\..\\dbin\\docfx\\docfx.exe init -q", shell=True)))

                src_files = os.listdir(target_docfx_yaml_directory)
                for file_name in src_files:
                    full_file_name = os.path.join(target_docfx_yaml_directory, file_name)
                    if os.path.isfile(full_file_name):
                        shutil.copy(full_file_name, os.path.join(docpath, "docfx_project", "api"))

                if operating_system in (OperatingSystem.macos, OperatingSystem.linux):
                    project_path = os.path.join(docpath, "docfx_project")
                    print(Util.pretty_stdout(subprocess.check_output(
                        "cd " + project_path + " && mono ./../../dbin/docfx/docfx.exe", shell=True)))

                site_path = os.path.join(project_path, "_site")
                copy_tree(site_path, docpath)

                shutil.rmtree(project_path)

                Util.cleanup_artifacts()
            else:
                print("[error] Could not work with DocFX. HTML output was not produced.")

class Util():
    '''
    Utility class that has a number of miscellaneous functions.
    '''

    @staticmethod
    def pretty_stdout(stdout):
        '''Prettify the standard output.'''

        output = str(stdout)
        output = output.split('\\n')
        for line in output:
            print(line)

    @staticmethod
    def cleanup_artifacts():
        '''Removes the unnecessary post-processing files.'''

        if os.path.exists(DOCFX_FILE_NAME):
            os.remove(DOCFX_FILE_NAME)
        if os.path.exists(BINARY_DIRECTORY):
            shutil.rmtree(BINARY_DIRECTORY)
        if os.path.exists(VIRTUAL_ENVIRONMENT_DIRECTORY):
            shutil.rmtree(VIRTUAL_ENVIRONMENT_DIRECTORY)

    @staticmethod
    def validate_url(url):
        '''Checks if the URL given to the tool is valid.'''

        # This is taken from Stack Overflow: https://stackoverflow.com/a/7160778
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain
            r'localhost|' #localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' #or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return re.match(regex, url) is not None

    @staticmethod
    def docfx_exists(auto_install=False):
        '''Check if DocFX exists on the system.'''

        if os.path.exists(os.path.join(BINARY_DIRECTORY, "docfx", "docfx.exe")):
            return True

        if auto_install:
            print('[info] Downloading and extracting DocFX...')
            urllib.request.urlretrieve(
                "https://github.com/dotnet/docfx/releases/download/v2.47/docfx.zip",
                DOCFX_FILE_NAME)
            with zipfile.ZipFile(DOCFX_FILE_NAME, "r") as zip_ref:
                zip_ref.extractall(os.path.join(BINARY_DIRECTORY, "docfx"))
            return True
        return False

    @staticmethod
    def shell_command_exists(command):
        '''Check if a command exists in the shell.'''

        return shutil.which(command) is not None

    @staticmethod
    def get_operating_system():
        '''Get the operating system context for the tool.'''

        if sys.platform in("linux", "linux2"):
            return OperatingSystem.linux
        elif sys.platform == "darwin":
            return OperatingSystem.macos
        elif sys.platform in ("win32", "cygwin"):
            return OperatingSystem.windows

        return OperatingSystem.other

    @staticmethod
    def folderize_package_name(package_name):
        split_name = re.findall(r"[\w']+", package_name)
        return os.path.join(*split_name)
        