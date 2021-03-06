#!/usr/bin/env python
# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

""" Run the WebKit tests. """

from build_step import BuildStep, BuildStepWarning
from utils import shell_utils
import os
import sys


class ChromeDRTCanaryRunWebkitTests(BuildStep):
  def __init__(self, timeout=16800, no_output_timeout=16800, **kwargs):
    super(ChromeDRTCanaryRunWebkitTests, self).__init__(
        timeout=timeout, no_output_timeout=no_output_timeout, **kwargs)

  def _Run(self):
    test_script_path = os.path.join('webkit', 'tools', 'layout_tests',
                                    'run_webkit_tests.sh')
    cmd = [
        test_script_path, '--build-directory', 'out', '--nocheck-sys-deps',
        '--additional-platform-directory=%s' %
            self._flavor_utils.baseline_dir,
        '--no-show-results'
    ]
    if 'new_baseline' in self._args:
      cmd.append('--new-baseline')
    if self._configuration == 'Debug':
      cmd.append('--debug')
    if 'write_results' in self._args:
      cmd.append('--results-directory=%s' % self._flavor_utils.result_dir)
    try:
      # Temporarily making this build step a no-op. Details are in
      # https://code.google.com/p/skia/issues/detail?id=2394
      # shell_utils.run(cmd)
      pass
    except Exception as e:
      # Allow this step to fail with a warning, since we expect to see a lot of
      # failures which aren't our fault. Instead, we care about the diffs.
      raise BuildStepWarning(e)


if '__main__' == __name__:
  sys.exit(BuildStep.RunBuildStep(ChromeDRTCanaryRunWebkitTests))
