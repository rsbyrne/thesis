#!/bin/bash

sudo apt update
sudo apt-get update

sudo pip3 install --no-cache-dir -U Whoosh # will be in Everest Dockerfile
sudo apt-get install -y imagemagick # will be in Everest Dockerfile

# Publishing
sudo apt-get install -y pandoc
sudo pip3 install --no-cache-dir -U jupyter-book
sudo pip3 install --no-cache-dir -U sphinxcontrib-bibtex
sudo pip3 install --no-cache-dir -U bibtexparser
sudo pip3 install --no-cache-dir -U ghp-import
sudo pip3 install --no-cache-dir -U myst-parser
sudo pip3 install --no-cache-dir -U sphinx
sudo pip3 install --no-cache-dir -U myst-nb
sudo pip3 install --no-cache-dir -U pyyaml
sudo pip3 install --no-cache-dir -U jupyterbook-latex

# Needed for LaTeX in matplotlibe
sudo apt install -y dvipng
sudo apt install -y cm-super
sudo apt install -y texlive-latex-extra

# Needed for LaTeX building
sudo apt install -y \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-fonts-extra \
  texlive-xetex \
  latexmk
