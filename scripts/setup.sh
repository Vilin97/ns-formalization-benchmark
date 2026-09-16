#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
(cd oai && lake exe cache get)
mkdir -p leanpool/.lake
if [ ! -e leanpool/.lake/packages ]; then
  ln -s ../../oai/.lake/packages leanpool/.lake/packages
fi
(cd leanpool && lake env lean --version)
