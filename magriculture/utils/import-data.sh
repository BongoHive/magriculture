#!/bin/bash
./manage.py fncs_import_crops --filename=./sample_data/t_crop_types.xls && \
./manage.py fncs_import_crop_units --filename=./sample_data/t_CropType_Units.xls && \
./manage.py fncs_import_provinces --filename=./sample_data/t_province.xls && \
./manage.py fncs_import_rpi_areas --filename=./sample_data/t_rpi_area.xls && \
./manage.py fncs_import_districts --filename=./sample_data/t_district.xls && \
./manage.py fncs_import_wards --filename=./sample_data/t_wards.xls && \
./manage.py fncs_import_markets --filename=./sample_data/t_Markets.xls && \
./manage.py fncs_import_farmers --filename=./sample_data/t_farmer_details.xls && \
./manage.py fncs_import_farmer_groups --filename=./sample_data/t_farmers_groups.xls && \
./manage.py fncs_import_farmer_wards --filename=./sample_data/t_farmers_wards.xls && \
./manage.py fncs_import_agents --filename="./sample_data/market agent pilot sheet-updated.xls" && \
true