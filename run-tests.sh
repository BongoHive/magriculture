#!/bin/bash
virtualenv --no-site-packages ve && \
source ve/bin/activate && \
    pip install -r magriculture/config/requirements.pip && \
    find ./magriculture -name '*.pyc' -delete && \
    cd magriculture && \
    ./manage.py test fncs --with-coverage --cover-erase --cover-package=magriculture --cover-html --with-xunit && \
    coverage xml --omit="ve/*" && \
    cd ../
    (pyflakes magriculture/ > pyflakes.log || true) && \
    (pep8 magriculture/ > pep8.log || true ) && \
deactivate
