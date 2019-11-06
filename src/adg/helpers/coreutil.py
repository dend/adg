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
from distutils.dir_util import copy_tree

virtual_environment_directory = "dtemp"
docfx_file_name = "temp_docfx.zip"
binary_directory = "dbin"

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
    def docfx_exists(auto_install = False):
        if (os.path.exists(os.path.join(binary_directory, "docfx", "docfx.exe"))):
            return True
        else:
            if auto_install:
                print('[info] Downloading and extracting DocFX...')
                urllib.request.urlretrieve("https://github.com/dotnet/docfx/releases/download/v2.47/docfx.zip", docfx_file_name)
                with zipfile.ZipFile(docfx_file_name, "r") as zip_ref:
                    zip_ref.extractall(os.path.join(binary_directory, "docfx"))
                return True
            return False

    @staticmethod
    def shell_command_exists(command):
        return shutil.which(command) is not None

class LibraryProcessor(object):
    @staticmethod
    def process_libraries(libraries, platform, docpath, out_format):
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
                    LibraryDocumenter.document_python_library(library, docpath, out_format)
                    
                    # Perform cleanup and just remove the folder where the virtual environment was set up.
                    #shutil.rmtree('dtemp')

class LibraryDocumenter(object):
    @staticmethod
    def document_python_library(library, docpath, out_format):
        print (f'[info] Attempting to document {library} from PyPI.')
        true_docpath = docpath
        if not docpath:
            true_docpath = os.getcwd()

        if not os.path.exists(true_docpath):
            os.mkdir(true_docpath)

        # Make sure that we install the documentation pre-requisites. These are the tools that will generate the final output.
        LibraryInstaller.install_python_library("sphinx-docfx-yaml")

        folderized_package = library.replace("-", "/")
        python_package_folder = os.listdir(os.path.join(virtual_environment_directory, "lib"))[0]

        target_site_packages_directory = os.path.join(virtual_environment_directory, "lib", python_package_folder, "site-packages")
        target_library_directory = os.path.join(target_site_packages_directory, folderized_package)
        target_docfx_yaml_directory = os.path.join(target_library_directory, "_build", "docfx_yaml")

        sphinx_quickstart_path = os.path.join("bin", "sphinx-quickstart")
        sphinx_apidoc_path = os.path.join("bin", "sphinx-apidoc")
        sphinx_build_path = os.path.join("bin", "sphinx-build")

        print(subprocess.check_output("cd " + target_library_directory + f" && ./../../../../../{sphinx_quickstart_path} -q -p 'adg' -a 'automated' -v '1.0'", shell=True))

        # We need to update the configuration file for Sphinx, to make sure that we're documenting the right library.
        configuration_file = os.path.join(target_library_directory, "conf.py")
        filedata = ''
        with open(configuration_file, 'r') as file :
            filedata = file.read()

        filedata = filedata.replace("extensions = []", "extensions = ['sphinx.ext.autodoc', 'docfx_yaml.extension']")

        import_combination = "import os\nimport sys\n"

        directories = [x for x in os.listdir(target_site_packages_directory) if os.path.isdir(os.path.join(target_site_packages_directory,x))]
        for directory in directories:
            if (not directory.startswith("_")):
                import_combination += f"sys.path.append(os.path.abspath('../../{directory}'))\n"

        filedata = filedata.replace("# import os", import_combination)

        with open(configuration_file, 'w') as file:
            file.write(filedata)

        print(subprocess.check_output("cd " + target_library_directory + f" && ./../../../../../{sphinx_apidoc_path} . -o . --module-first --no-headings --no-toc --implicit-namespaces", shell=True))
        print(subprocess.check_output("cd " + target_library_directory + f" && ./../../../../../{sphinx_build_path} . _build", shell=True))

        # .lower() should likely be enough for a case-insensitive check since we are
        # working with a limited set of values. Otherwise, we would need to check .casefold().
        if out_format.lower() == 'yaml':
            src_files = os.listdir(target_docfx_yaml_directory)
            for file_name in src_files:
                full_file_name = os.path.join(target_docfx_yaml_directory, file_name)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, docpath)
        elif out_format.lower() == 'html':
            if PresenceVerifier.docfx_exists(auto_install = True):
                # DocFX exists. We can proceed.
                print(subprocess.check_output("cd " + docpath + " && mono ./../dbin/docfx/docfx.exe init -q", shell=True))

                src_files = os.listdir(target_docfx_yaml_directory)
                for file_name in src_files:
                    full_file_name = os.path.join(target_docfx_yaml_directory, file_name)
                    if os.path.isfile(full_file_name):
                        shutil.copy(full_file_name, os.path.join(docpath, "docfx_project", "api"))

                project_path = os.path.join(docpath, "docfx_project")
                print(Util.pretty_stdout(subprocess.check_output("cd " + project_path + " && mono ./../../dbin/docfx/docfx.exe", shell=True)))

                site_path = os.path.join(project_path, "_site")
                copy_tree(site_path, docpath)
                
                shutil.rmtree(project_path)

                Util.cleanup_artifacts()
            else:
                print("[error] Could not work with DocFX. HTML output was not produced.")

    # @staticmethod
    # def document_node_library(library, docpath):
    #     true_docpath = docpath
    #     if not docpath:
    #         true_docpath = os.getcwd()

    #     #process_result = subprocess.run(['pip3', 'list',], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

class Util(object):
    @staticmethod
    def pretty_stdout(stdout):
        output = str(stdout)
        output = output.split('\\n')
        for x in range(len(output)):
            print (output[x])
    
    @staticmethod
    def cleanup_artifacts():
        if os.path.exists(docfx_file_name):
            os.remove(docfx_file_name)
        if os.path.exists(binary_directory):
            shutil.rmtree(binary_directory)
        if os.path.exists(virtual_environment_directory):
            shutil.rmtree(virtual_environment_directory)
        