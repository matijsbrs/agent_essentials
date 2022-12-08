#!/bin/bash

sed -i 's/_version.*=.*/_version = "'`git tag | tail -n 1`'"/g' base.py
sed -i 's/_date.*=.*/_date = "'`date  +%d%m%Y`'"/g' base.py 

