function manage() {
    cd ${INSTALLDIR}/magriculture
    ${VENV}/bin/django-admin.py "$@" --settings=magriculture.settings
    cd -
}

manage syncdb --noinput --no-initial-data --migrate
manage collectstatic --noinput
