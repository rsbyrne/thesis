#!/bin/bash

sudo apt-get update

sudo pip3 install --no-cache-dir -U Whoosh

# Publishing
sudo apt-get install -y pandoc
sudo pip3 install --no-cache-dir -U jupyter-book
sudo pip3 install --no-cache-dir -U sphinxcontrib-bibtex
sudo pip3 install --no-cache-dir -U bibtexparser
sudo pip3 install --no-cache-dir -U ghp-import
sudo pip3 install --no-cache-dir -U myst-parser

# Needed for LaTeX building
sudo apt-get install -y \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-fonts-extra \
  texlive-xetex \
  latexmk