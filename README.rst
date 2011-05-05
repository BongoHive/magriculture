README
======

Create a virtualenv and install Vumi straight from the repository with pip::

    $ virtualenv --no-site-packages ve
    $ source ve/bin/activate
    (ve)$ pip install -r config/requirements.pip
    (ve)$ twistd 
    
As part of the list of twistd plugins you should see the `start_worker` and `start_webapp` twisted plugins.