#/bin/bash
set -eux

[[ -d ./venv ]]  # assert

# v0.32.0
drake=~/Downloads/drake-20210714-bionic.tar.gz
[[ -f ${drake} ]]  # assert

tar -xzf ${drake} -C ./venv --strip-components=1
