#!/bin/bash
#
# Setup all the master buildbot instances.
#
# Copyright 2012 Google Inc. All Rights Reserved.
# Author: rmistry@google.com (Ravi Mistry)

source vm_config.sh

for VM in $VM_MASTER_NAMES; do
  VM_COMPLETE_NAME="${VM_NAME_BASE}-${VM}-${ZONE_TAG}"

  echo """

================================================
Starting setup of ${VM_COMPLETE_NAME}.....
================================================

"""

  $GCOMPUTE_CMD ssh --ssh_user=default $VM_COMPLETE_NAME \
    "sudo apt-get update; " \
    "sudo apt-get install git make subversion postfix python-dev; " \
    "echo 'PATH=\"~/skia-master/depot_tools:/usr/local/sbin:/usr/sbin:/sbin:$PATH\"' >> ~/.bashrc; " \
    "echo 'alias m=\"cd ~/skia-master/buildbot/master\"' >> ~/.bashrc; " \
    "sudo easy_install --upgrade google-api-python-client; " \
    "sudo easy_install --upgrade pyOpenSSL; " \
    "sudo sh -c 'echo 127.0.0.1 smtp >> /etc/hosts'"

   echo """
Please manually ssh into ${VM_COMPLETE_NAME} from a different terminal and:
  Comment out the TLS parameters section in /etc/postfix/main.cf.

ssh cmd: ${GCOMPUTE_CMD} ssh --ssh_user=default ${VM_COMPLETE_NAME}
"""

  unset USER_INPUT
  echo "Please enter 'y' when you are ready to proceed."
  while [ "$USER_INPUT" != "y" ]; do
    read -n 1 USER_INPUT
  done

  $GCOMPUTE_CMD ssh --ssh_user=default $VM_COMPLETE_NAME \
    "mkdir ~/skia-master; " \
    "sudo /usr/share/google/safe_format_and_mount /dev/${VM}-disk-${ZONE_TAG} /home/default/skia-master; " \
    "cd ~/skia-master; " \
    "sudo chmod 777 -R .; " \
    "svn checkout http://src.chromium.org/svn/trunk/tools/depot_tools; " \
    "~/skia-master/depot_tools/gclient config https://skia.googlecode.com/svn/buildbot; " \
    "~/skia-master/depot_tools/gclient sync; "

done

