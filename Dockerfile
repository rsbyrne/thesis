FROM rsbyrne/everest
MAINTAINER https://github.com/rsbyrne/

USER root

ENV THESISDIR $MASTERUSERHOME/thesis
ADD . $THESISDIR
RUN chown -R $MASTERUSER $THESISDIR

# Python
ENV PYTHONPATH "$THESISDIR:${PYTHONPATH}"
ENV PYTHONPATH "$THESISDIR/resources:${PYTHONPATH}"

# Publishing
RUN pip3 install -u bibtexparser

USER $MASTERUSER
