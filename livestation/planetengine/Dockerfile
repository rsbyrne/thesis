FROM underworldcode/uw2cylindrical:cylindrical

USER root

RUN easy_install pip
RUN pip install --no-cache-dir -U h5py

RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y nano
RUN apt-get install -y ffmpeg

RUN pip install --no-cache-dir pandas
RUN pip install --no-cache-dir bokeh
RUN pip install --no-cache-dir Flask
RUN pip install --no-cache-dir dask[complete]
RUN pip install --no-cache-dir scikit-learn
RUN pip install --no-cache-dir tensorflow

ENV PYTHONPATH "${PYTHONPATH}:/home/jovyan/workspace"

USER $NB_USER

RUN umask 0000
