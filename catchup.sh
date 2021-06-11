#!/bin/bash

apt update
apt-get update

# Everest
pip3 install --no-cache-dir -U Whoosh # will be in Everest Dockerfile
apt-get install -y imagemagick # will be in Everest Dockerfile
pip3 install --no-cache-dir -U graphviz # will be in Everest Dockerfile

# Publishing
apt-get install -y pandoc
pip3 install --no-cache-dir -U jupyter-book
pip3 install --no-cache-dir -U sphinxcontrib-bibtex
pip3 install --no-cache-dir -U bibtexparser
pip3 install --no-cache-dir -U ghp-import
pip3 install --no-cache-dir -U myst-parser
pip3 install --no-cache-dir -U sphinx
pip3 install --no-cache-dir -U myst-nb
pip3 install --no-cache-dir -U pyyaml
pip3 install --no-cache-dir -U jupyterbook-latex

# Needed for LaTeX in matplotlib
apt install -y \
  dvipng \
  cm-super \
  texlive-latex-extra

# Needed for LaTeX building
apt install -y \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-fonts-extra \
  texlive-xetex \
  latexmk
