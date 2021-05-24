FROM rsbyrne/everest
MAINTAINER https://github.com/rsbyrne/

USER root

ENV THESISDIR $MASTERUSERHOME/thesis
ADD . $THESISDIR
RUN chown -R $MASTERUSER $THESISDIR

# for apt to be noninteractive
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

# Set timezone
# RUN \
#   ls /usr/share/zoneinfo && \
#   cp /usr/share/zoneinfo/Australia/Melbourne /etc/localtime && \
#   echo "Australia/Melbourne" > /etc/timezone && \

# Python
ENV PYTHONPATH "$THESISDIR:${PYTHONPATH}"
ENV PYTHONPATH "$THESISDIR/resources:${PYTHONPATH}"

# Needed for LaTeX building
RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
  tzdata \
  pandoc \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-fonts-extra \
  texlive-xetex \
  latexmk

# Publishing
RUN pip3 install -U --no-cache-dir \
  jupyter-book \
  bibtexparser \
  ghp-import \
  myst-parser \
  sphinxcontrib-bibtex

# Needed by Pyppeteer
# RUN rm -rf /var/lib/apt/lists/* && apt clean && apt update && apt install -y \
#   chromium-chromedriver
#   gconf-service \
#   libasound2 \
#   libatk1.0-0 \
#   libc6 \
#   libcairo2 \
#   libcups2 \
#   libdbus-1-3 \
#   libexpat1 \
#   libfontconfig1 \
#   libgcc1 \
#   libgconf-2-4 \
#   libgdk-pixbuf2.0-0 \
#   libglib2.0-0 \
#   libgtk-3-0 \
#   libnspr4 \
#   libpango-1.0-0 \
#   libpangocairo-1.0-0 \
#   libstdc++6 \
#   libx11-6 \
#   libx11-xcb1 \
#   libxcb1 \
#   libxcomposite1 \
#   libxcursor1 \
#   libxdamage1 \
#   libxext6 \
#   libxfixes3 \
#   libxi6 \
#   libxrandr2 \
#   libxrender1 \
#   libxss1 \
#   libxtst6 \
#   ca-certificates \
#   fonts-liberation \
#   libappindicator1 \
#   libnss3 \
#   lsb-release \
#   xdg-utils \
#   wget
# RUN pip3 install --no-cache-dir -U pyppeteer

USER $MASTERUSER
