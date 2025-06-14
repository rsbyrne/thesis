FROM ubuntu:hirsute-20210514
MAINTAINER https://github.com/rsbyrne/

ENV MASTERUSER morpheus
ENV MASTERPASSWD Matrix-1999!

# for apt to be noninteractive
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

# install with apt
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  gpgv2 \
  software-properties-common \
  dialog \
  sudo \
  vim \
  && rm -rf /var/lib/apt/lists/*

# configure master user
RUN useradd -p $(openssl passwd -1 $MASTERPASSWD) $MASTERUSER && \
  usermod -aG sudo $MASTERUSER && \
  groupadd workers && \
  usermod -g workers $MASTERUSER

# configure user directories
ENV MASTERUSERHOME /home/$MASTERUSER
RUN mkdir $MASTERUSERHOME
ENV WORKSPACE $MASTERUSERHOME/workspace
RUN mkdir $WORKSPACE
ENV TOOLS $MASTERUSERHOME/tools
RUN mkdir $TOOLS
ENV MOUNTDIR $WORKSPACE/mount
VOLUME $MOUNTDIR
RUN chown -R $MASTERUSER $MASTERUSERHOME
ENV PATH "${PATH}:$MASTERUSERHOME/.local/bin"

# set up passwordless sudo for master user
RUN echo $MASTERUSER 'ALL = (ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

# install other softwares
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  apt-utils \
  curl \
  git \
  man \
  nano \
  wget \
  && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt /tmp/
# RUN pip install -y -r requirements.txt

# install Python3.10
#RUN add-apt-repository -y ppa:deadsnakes/ppa
#RUN apt install -y python3.10
#RUN add-apt-repository -y --remove ppa:deadsnakes/ppa

# install Python stuff
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  python3-venv \
  python3-pip
ENV PYTHONPATH "$BASEDIR:${PYTHONPATH}"
ENV PYTHONPATH "$WORKSPACE:${PYTHONPATH}"
ENV PYTHONPATH "$MOUNTDIR:${PYTHONPATH}"

# change to master user
USER $MASTERUSER
WORKDIR $MASTERUSERHOME

# aliases
RUN echo "alias python=python3" >> ~/.bashrc && \
  echo "alias pip=pip3" >> ~/.bashrc

USER root

# Python
ENV PYTHONPATH "$EVERESTDIR:${PYTHONPATH}"

# Production
RUN pip3 install -U --no-cache-dir \
  mypy \
  pytest

# CLI
RUN pip3 install -U --no-cache-dir click

# Convenience
# https://whoosh.readthedocs.io/en/latest/
RUN pip3 install --no-cache-dir -U Whoosh

# MPI
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  libopenmpi-dev
RUN pip3 install --no-cache-dir mpi4py
ENV OMPI_MCA_btl_vader_single_copy_mechanism "none"

# Debugging
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  cloc \
  graphviz \
  && rm -rf /var/lib/apt/lists/*
RUN pip3 install -U --no-cache-dir \
  objgraph \
  xdot

# Visualisation
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  cm-super \
  dvipng \
  ffmpeg \
  imagemagick \
  texlive-latex-extra \
  && rm -rf /var/lib/apt/lists/*
RUN pip3 install -U --no-cache-dir \
  matplotlib \
  Pillow \
  graphviz

# Data
RUN pip3 install -U --no-cache-dir \
  dask[complete] \
  diversipy \
  h5py \
  numba \
  pandas \
  scipy \
  xarray[complete]

# Machine Learning
RUN pip3 install -U --no-cache-dir \
  scikit-learn
#RUN pip3 install --no-cache-dir torch torchvision
#RUN pip3 install --no-cache-dir fastai

# Networking
RUN pip3 install -U --no-cache-dir \
  paramiko

# Maths
RUN pip3 install -U --no-cache-dir \
  mpmath \
  sympy \
  more-itertools

# Productivity
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  nodejs \
  npm \
  && rm -rf /var/lib/apt/lists/*
RUN pip3 install -U --no-cache-dir \
#  flake8 \
  jupyterlab
#  jupyterlab-lsp \
#  'python-lsp-server[all]' \
#  pyls-flake8
#RUN jupyter labextension install jupyterlab-flake8

# Finish
RUN apt update -y && apt upgrade -y

ENV EVERESTDIR $MASTERUSERHOME/everest
ADD . $EVERESTDIR
RUN chown -R $MASTERUSER $EVERESTDIR

USER $MASTERUSER
