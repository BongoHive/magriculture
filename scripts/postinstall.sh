function manage() {
    cd ${INSTALLDIR}/magriculture
    ${VENV}/bin/python ${INSTALLDIR}/magriculture/manage.py "$@"
    cd -
}

manage syncdb --noinput --no-initial-data --migrate
manage collectstatic --noinput
