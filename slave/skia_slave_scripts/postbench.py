#!/usr/bin/env python
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

""" Step to run after the benchmarking steps. """

from build_step import BuildStep
import sys


class PostBench(BuildStep):
  def _Run(self):
    if self._perf_data_dir:
      self._flavor_utils.CopyDirectoryContentsToHost(
          self._device_dirs.PerfDir(), self._perf_data_dir)


if '__main__' == __name__:
  sys.exit(BuildStep.RunBuildStep(PostBench))