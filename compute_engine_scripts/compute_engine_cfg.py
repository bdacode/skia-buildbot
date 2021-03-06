#!/usr/bin/env python
# Copyright (c) 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""This file contains config constants for the chromecompute GCE instances."""

import os
import types


PROJECT_USER = 'default'
SKIA_NETWORK_NAME = 'skia'
SKIA_REPO_DIR = '/home/%s/storage/skia-repo' % PROJECT_USER
SCOPES = 'https://www.googleapis.com/auth/devstorage.full_control'
SKIA_BOT_IMAGE_NAME = 'skiatelemetry-6-0-ubuntu1310'
SKIA_BOT_MACHINE_TYPE = 'lmt-n1-standard-8-d'
IP_ADDRESS_WITHOUT_MACHINE_PART = '108.170.192'
VM_BOT_NAME = 'skia-vm'

# The Project ID is found in the Compute tab of the dev console.
# https://cloud.google.com/console#c=p&pid=182615506979
PROJECT_ID = 'google.com:chromecompute'

# The (Shared Fate) Zone is conceptually equivalent to a data center cell. VM
# instances live in a zone.
#
# We flip the default one as required by PCRs in bigcluster.
ZONE_TAG = os.environ.get('ZONE_TAG', 'b')
ZONE = 'us-central2-%s' % ZONE_TAG

# The below constants determine which instances the delete and create/setup
# scripts apply to.
# Eg1: VM_BOT_COUNT_START=1 VM_BOT_COUNT_END=5 vm_create_setup_instances.sh
#   The above command will create and setup skia-vm-001 to skia-vm-005.
# Eg2: VM_BOT_COUNT_START=1 VM_BOT_COUNT_END=1 vm_create_setup_instances.sh
#   The above command will create and setup only skia-vm-001.
VM_BOT_COUNT_START = os.environ.get('VM_BOT_COUNT_START', 1)
VM_BOT_COUNT_END = os.environ.get('VM_BOT_COUNT_END', 100)

# Recreate SKPs bot constants.
VM_RECREATESKPS_BOT_NAME = 'skia-recreate-skps-bot'
VM_RECREATESKPS_BOT_IP_ADDRESS = '%s.101' % IP_ADDRESS_WITHOUT_MACHINE_PART


if __name__ == '__main__':
  # Set all above constants as environment variables if this module is called as
  # a script.
  for var in vars().keys():
    # Ignore if the var is a system var or a module.
    if not var.startswith('__') and not type(vars()[var]) == types.ModuleType:
      print 'export %s=%s' % (var, vars()[var])

