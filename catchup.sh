#!/bin/bash

sudo apt update
sudo apt-get update

# Needed for LaTeX building
sudo apt-get install -y \
  jq

sudo apt install python-is-python3

sudo pip install -U --no-cache-dir --break-system-packages \
  bibtexparser \
  ghp-import \
  myst-parser \
  sphinxcontrib-bibtex \
  sphinx \
  myst-nb \
  jupytext \
  mystmd \
  pyyaml \
  jupyterlab_myst

sudo jupyter server extension enable jupytext