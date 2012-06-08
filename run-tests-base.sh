#!/bin/sh

# NOTE: This assumes we're in an appropriate virtualenv.

find ./magriculture -name '*.pyc' -delete

# use fast tests (i.e. sqlite in-memory db) by default
export MAGRICULTURE_FAST_TESTS=1

# These are expected to be Twisted tests that trial should run.
vumi_tests="magriculture/workers"

eval $COVERAGE_COMMAND `which trial` ${vumi_tests}
r1=$?
eval $COVERAGE_COMMAND `which django-admin.py` test --settings=magriculture.testsettings
r2=$?

exit $(($r1 + $r2))
