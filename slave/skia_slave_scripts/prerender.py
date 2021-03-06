#!/usr/bin/env python
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

""" Prepare runtime resources that are needed by Test builders but not
    Bench builders. """

from build_step import BuildStep
import build_step
# builder_name_schema must be imported after build_step so the PYTHONPATH will
# be set properly to import it.
import builder_name_schema
import os
import sys


class PreRender(BuildStep):

  def _Run(self):
    # Prepare directory to hold GM expectations.
    self._flavor_utils.CreateCleanDeviceDirectory(
        self._device_dirs.GMExpectedDir())

    # Push the GM expectations JSON file to the device.
    device_gm_expectations_path = self._flavor_utils.DevicePathJoin(
        self._device_dirs.GMExpectedDir(), build_step.GM_EXPECTATIONS_FILENAME)
    repo_gm_expectations_path = os.path.join(
        self._gm_expected_dir, build_step.GM_EXPECTATIONS_FILENAME)
    if os.path.exists(repo_gm_expectations_path):
      print 'Pushing GM expectations from %s on host to %s on device...' % (
          repo_gm_expectations_path, device_gm_expectations_path)
      self._flavor_utils.PushFileToDevice(repo_gm_expectations_path,
                                          device_gm_expectations_path)
    else:
      print('Missing GM expectations file %s' % repo_gm_expectations_path)

    # Push GM's ignore_failures_file to the device.
    device_ignore_failures_path = self._flavor_utils.DevicePathJoin(
        self._device_dirs.GMExpectedDir(), build_step.GM_IGNORE_FAILURES_FILE)
    repo_ignore_failures_path = os.path.join(
        self._gm_expected_dir, os.pardir, build_step.GM_IGNORE_FAILURES_FILE)
    if os.path.exists(repo_ignore_failures_path):
      print ('Pushing ignore_failures_file from %s on host to %s on device...'
             % (repo_ignore_failures_path, device_ignore_failures_path))
      self._flavor_utils.PushFileToDevice(repo_ignore_failures_path,
                                          device_ignore_failures_path)
    else:
      print('Missing ignore_failures_file %s' % repo_ignore_failures_path)

    # Prepare directory to hold GM actuals.
    self._flavor_utils.CreateCleanHostDirectory(self._gm_actual_dir)
    self._flavor_utils.CreateCleanDeviceDirectory(
        self._flavor_utils.DevicePathJoin(self._device_dirs.GMActualDir(),
                                          self._builder_name))
    self._flavor_utils.CreateCleanHostDirectory(self.skp_out_dir)
    self._flavor_utils.CreateCleanDeviceDirectory(self._device_dirs.SKPOutDir())

    # Copy expectations file and images to decode in skimage to device.
    self._flavor_utils.CreateCleanDeviceDirectory(
        self._device_dirs.SKImageExpectedDir())
    skimage_subdir = builder_name_schema.GetWaterfallBot(self._builder_name)
    skimage_expected_filename = build_step.GM_EXPECTATIONS_FILENAME

    skimage_host_expectations = os.path.join(self._skimage_expected_dir,
                                             skimage_subdir,
                                             skimage_expected_filename)

    if os.path.exists(skimage_host_expectations):
      skimage_device_subdir = self._flavor_utils.DevicePathJoin(
          self._device_dirs.SKImageExpectedDir(),
          skimage_subdir)
      skimage_device_expectations = self._flavor_utils.DevicePathJoin(
          skimage_device_subdir, skimage_expected_filename)
      # For builders without an attached device, PushFileToDevice will fail
      # when attempting to copy a file to itself. In this case, there is no
      # need to copy. Only do the push when there is an attached device,
      # which corresponds to the case that the filepaths are equal.
      # TODO(scroggo): Once
      # https://code.google.com/p/skia/issues/detail?id=1571 is fixed, this
      # check can go away.
      if skimage_device_expectations != skimage_host_expectations:
        # Create the subdir on the device.
        self._flavor_utils.CreateCleanDeviceDirectory(skimage_device_subdir)
        self._flavor_utils.PushFileToDevice(skimage_host_expectations,
            skimage_device_expectations)

    self._flavor_utils.CopyDirectoryContentsToDevice(
        self._skimage_in_dir, self._device_dirs.SKImageInDir())


    # Create a directory for the output of skimage
    self._flavor_utils.CreateCleanHostDirectory(self._skimage_out_dir)
    self._flavor_utils.CreateCleanDeviceDirectory(
        self._device_dirs.SKImageOutDir())


if '__main__' == __name__:
  sys.exit(BuildStep.RunBuildStep(PreRender))
