#!/bin/bash
dropdb magriculture
createdb magriculture
./manage.py syncdb --migrate --noinput
echo "Creating superuser"
./manage.py createsuperuser