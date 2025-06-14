FROM ubuntu:groovy-20210115
MAINTAINER https://github.com/rsbyrne/

ENV MASTERUSER morpheus
ENV MASTERPASSWD Matrix-1999!

# install softwares required for subsequent steps
RUN apt update -y
RUN apt upgrade -y
RUN apt install -y software-properties-common
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y software-properties-common
RUN apt-get install -y sudo
RUN apt-get install -y vim

# configure master user
RUN useradd -p $(openssl passwd -1 $MASTERPASSWD) $MASTERUSER
RUN usermod -aG sudo $MASTERUSER
RUN groupadd workers
RUN usermod -g workers $MASTERUSER

# configure user directories
ENV MASTERUSERHOME /home/$MASTERUSER
RUN mkdir $MASTERUSERHOME
ENV WORKSPACE $MASTERUSERHOME/workspace
RUN mkdir $WORKSPACE
ENV TOOLS $MASTERUSERHOME/tools
RUN mkdir $TOOLS
ENV MOUNTDIR $WORKSPACE/mount
VOLUME $MOUNTDIR
ENV BASEDIR $MASTERUSERHOME/base
ADD . $BASEDIR
RUN chown -R $MASTERUSER $MASTERUSERHOME
ENV PATH "${PATH}:$MASTERUSERHOME/.local/bin"

# set up passwordless sudo for master user
RUN echo $MASTERUSER 'ALL = (ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

# install other softwares
RUN apt-get install -y apt-utils
RUN apt-get install -y man
RUN apt-get install -y curl
RUN apt-get install -y wget
RUN apt-get install -y git
RUN apt-get install -y nano
RUN apt-get install -y apache2

# install Python3.9
#RUN apt update
#RUN apt install -y software-properties-common
#RUN add-apt-repository -y ppa:deadsnakes/ppa
#RUN apt install -y python3.9
#RUN add-apt-repository -y --remove ppa:deadsnakes/ppa

# install Python stuff
RUN apt-get install -y python3-venv
RUN apt-get install -y python3-pip
ENV PYTHONPATH "$BASEDIR:${PYTHONPATH}"
ENV PYTHONPATH "$WORKSPACE:${PYTHONPATH}"
ENV PYTHONPATH "$MOUNTDIR:${PYTHONPATH}"

# change to master user
USER $MASTERUSER
WORKDIR $MASTERUSERHOME

# aliases
RUN echo "alias python=python3" >> ~/.bashrc
RUN echo "alias pip=pip3" >> ~/.bashrc
#RUN source ~/.bashrc

# junk
#RUN apt update
