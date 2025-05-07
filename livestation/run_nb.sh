#!/bin/bash
jupyter notebook --no-browser --allow-root --port=7777 --ip='0.0.0.0' &> /home/jovyan/workspace/nb.log
