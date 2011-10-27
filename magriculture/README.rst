Installation
============

::

  $ virtualenv --no-site-packages ve
  $ source ve/bin/activate
  (ve)$ cd magriculture
  (ve)$ pip install -r config/requirements.pip
  (ve)$ ./manage.py syncdb --noinput
  (ve)$ ./manage.py migrate
  (ve)$ ./manage.py createsuperuser
  (ve)$ ./manage.py fncs_make_agent --username=<name of your super user>
  (ve)$ ./manage.py fncs_make_marketmonitor --username=<name of your super user>
  (ve)$ ./manage.py fncs_create_sample_farmers
  (ve)$ ./manage.py fncs_create_sample_transactions
  (ve)$ ./manage.py fncs_create_random_notes
  (ve)$ ./manage.py fncs_create_random_messages
  (ve)$ ./manage.py runserver

Tests
=====

We use nose to run our Django tests

::

  (ve)$ ./manage.py test fncs
