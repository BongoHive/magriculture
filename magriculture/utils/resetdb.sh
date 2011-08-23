#!/bin/bash
dropdb --username magriculture -W --host localhost magriculture
createdb --username magriculture -W --host localhost magriculture
./manage.py syncdb --migrate --noinput
echo "Creating superuser"
./manage.py createsuperuser