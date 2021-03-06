#!/bin/bash
#
# Runs a Lua script from Google Storage on the SKP files on this slave.
#
# The script should be run from the cluster-telemetry-slave GCE instance's
# /b/skia-repo/buildbot/cluster_telemetry/telemetry_slave_scripts
# directory.
#
# Copyright 2013 Google Inc. All Rights Reserved.
# Author: rmistry@google.com (Ravi Mistry)

if [ $# -ne 5 ]; then
  echo
  echo "Usage: `basename $0` 1 gs://chromium-skia-gm/telemetry/lua_scripts/test.lua" \
    "rmistry-2013-05-24.07-34-05"
  echo
  echo "The first argument is the slave_num of this telemetry slave."
  echo "The second argument is the Google Storage location of the Lua script."
  echo "The third argument is a unique run id (typically requester + timestamp)."
  echo "The fourth argument is the type of pagesets to create from the 1M list" \
       "Eg: All, Filtered, 100k, 10k, Deeplinks."
  echo "The fifth argument is the name of the directory where the chromium" \
       "build which will be used for this run is stored."
  echo
  exit 1
fi

SLAVE_NUM=$1
LUA_SCRIPT_GS_LOCATION=$2
RUN_ID=$3
PAGESETS_TYPE=$4
CHROMIUM_BUILD_DIR=$5

source vm_utils.sh

WORKER_FILE=LUA.$RUN_ID
LUA_FILE=$RUN_ID.lua
LUA_OUTPUT_FILE=$RUN_ID.lua-output
create_worker_file $WORKER_FILE

# Sync trunk.
cd /b/skia-repo/trunk
for i in {1..3}; do /b/depot_tools/gclient sync && break || sleep 2; done

# Build tools.
make clean
GYP_DEFINES="skia_warnings_as_errors=0" make tools BUILDTYPE=Release

# Download the SKP files from Google Storage if the local TIMESTAMP is out of date.
mkdir -p /b/storage/skps/$PAGESETS_TYPE/$CHROMIUM_BUILD_DIR/
are_timestamps_equal /b/storage/skps/$PAGESETS_TYPE/$CHROMIUM_BUILD_DIR gs://chromium-skia-gm/telemetry/skps/slave$SLAVE_NUM/$PAGESETS_TYPE/$CHROMIUM_BUILD_DIR
if [ $? -eq 1 ]; then
  gsutil cp gs://chromium-skia-gm/telemetry/skps/slave$SLAVE_NUM/$PAGESETS_TYPE/$CHROMIUM_BUILD_DIR/* /b/storage/skps/$PAGESETS_TYPE/$CHROMIUM_BUILD_DIR/
fi

# Copy the lua script from Google Storage to /tmp.
gsutil cp $LUA_SCRIPT_GS_LOCATION /tmp/$LUA_FILE

# Run lua_pictures.
cd out/Release
./lua_pictures --skpPath /b/storage/skps/$PAGESETS_TYPE/$CHROMIUM_BUILD_DIR/ --luaFile /tmp/$LUA_FILE > /tmp/$LUA_OUTPUT_FILE

# Copy the output of the lua script to Google Storage.
gsutil cp /tmp/$LUA_OUTPUT_FILE gs://chromium-skia-gm/telemetry/lua-outputs/slave$SLAVE_NUM/$LUA_OUTPUT_FILE

# Clean up logs and the worker file.
rm -rf /tmp/*${RUN_ID}*
delete_worker_file $WORKER_FILE
