#!/bin/bash

# Copyright 2025 Cloudera Government Solutions, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

pip install --upgrade pip

pip install --log 1_session-install-deps/pip-req.log -r 2_session-install-dependencies/requirements.txt

pip install tokenizers==0.13.0