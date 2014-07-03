#!/bin/bash

cp -a magriculture ./build/

rm -rf ./build/etc/
rm -rf ./build/.git

pip install -r magriculture/requirements.pip
