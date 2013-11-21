#!/bin/sh

# NOTE: This assumes we're in an appropriate virtualenv.

find ./magriculture -name '*.pyc' -delete

# use fast tests (i.e. sqlite in-memory db) by default
export MAGRICULTURE_FAST_TESTS=1

eval python manage.py test
r1=$?
eval cd go-js && npm install . && npm test
r2=$?
exit $(($r1 + $r2))
