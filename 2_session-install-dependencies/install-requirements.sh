#!/bin/bash

pip install --upgrade pip

pip install --log 1_session-install-deps/pip-req.log -r 2_session-install-dependencies/requirements.txt

pip install tokenizers==0.13.0