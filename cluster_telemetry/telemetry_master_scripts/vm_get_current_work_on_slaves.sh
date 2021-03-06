#!/bin/bash
#
# Prints the current tasks performed by all slaves.
#
# The script should be run from the cluster-telemetry-master GCE instance's
# /b/skia-repo/buildbot/cluster_telemetry/telemetry_master_scripts
# directory.
#
# Copyright 2013 Google Inc. All Rights Reserved.
# Author: rmistry@google.com (Ravi Mistry)

source ../config.sh
source vm_utils.sh

# Update buildbot.
gclient sync

for SLAVE_NUM in $(seq 1 $NUM_SLAVES); do
  result=$(get_current_work_on_slave $SLAVE_NUM)
  if [ "$result" ]; then
    echo "===== cluster-telemetry-worker$SLAVE_NUM is currently running: $result ====="
  fi
done

