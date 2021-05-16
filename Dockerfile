FROM rsbyrne/everest
MAINTAINER https://github.com/rsbyrne/

USER root

ENV THESISDIR $MASTERUSERHOME/thesis
ADD . $THESISDIR
RUN chown -R $MASTERUSER $THESISDIR

RUN apt update -y
RUN apt-get update -y

# for apt to be noninteractive
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

# Set timezone
RUN \
  ls /usr/share/zoneinfo && \
  cp /usr/share/zoneinfo/Australia/Melbourne /etc/localtime && \
  echo "Australia/Melbourne" > /etc/timezone && \
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata

# Python
ENV PYTHONPATH "$THESISDIR:${PYTHONPATH}"
ENV PYTHONPATH "$THESISDIR/resources:${PYTHONPATH}"

# User
RUN apt-get install -y dialog
# RUN unminimize

# Publishing
RUN apt-get install -y pandoc
RUN pip3 install --no-cache-dir -U jupyter-book
RUN pip3 install --no-cache-dir -U sphinxcontrib-bibtex
RUN pip3 install --no-cache-dir -U bibtexparser
RUN pip3 install --no-cache-dir -U ghp-import
RUN pip3 install --no-cache-dir -U myst-parser

# Needed for LaTeX building
RUN apt-get install -y \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-fonts-extra \
  texlive-xetex \
  latexmk

Needed by Pyppeteer
RUN apt-get install -y chromium-chromedriver
RUN apt install -y \
  gconf-service \
  libasound2 \
  libatk1.0-0 \
  libc6 \
  libcairo2 \
  libcups2 \
  libdbus-1-3 \
  libexpat1 \
  libfontconfig1 \
  libgcc1 \
  libgconf-2-4 \
  libgdk-pixbuf2.0-0 \
  libglib2.0-0 \
  libgtk-3-0 \
  libnspr4 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libstdc++6 \
  libx11-6 \
  libx11-xcb1 \
  libxcb1 \
  libxcomposite1 \
  libxcursor1 \
  libxdamage1 \
  libxext6 \
  libxfixes3 \
  libxi6 \
  libxrandr2 \
  libxrender1 \
  libxss1 \
  libxtst6 \
  ca-certificates \
  fonts-liberation \
  libappindicator1 \
  libnss3 \
  lsb-release \
  xdg-utils \
  wget
RUN pip3 install --no-cache-dir -U pyppeteer

USER $MASTERUSER
