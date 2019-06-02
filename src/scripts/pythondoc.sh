#!/bin/bash

cd $1
cd $2
export PATH="$PATH:$HOME/Library/Python/3.7/bin"
sphinx-quickstart -q -p '_adg' -a 'automated' -v '1.0'
sed -i .bak "s/extensions.*/extensions = ['sphinx.ext.autodoc', 'docfx_yaml.extension']/g" conf.py
IMPORT_COMBINATION='import os\nimport sys\n'
for combo in $(ls -d */ | cut -f1 -d"/"); do IMPORT_COMBINATION+="sys.path.append(os.path.abspath('$combo'))\n"; done
echo $IMPORT_COMBINATION | cat - conf.py > temp && mv temp conf.py
cat conf.py
sphinx-apidoc . -o . --module-first --no-headings --no-toc --implicit-namespaces
sphinx-build . _build
ls _build/docfx_yaml
pwd
cp -a _build/docfx_yaml/. ../../_docs/docfx_project/api/
cd ../../_docs/docfx_project
mono ../../_docfx/docfx.exe